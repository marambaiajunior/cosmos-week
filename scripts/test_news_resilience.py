"""Regression cases based on the failed GitHub Actions run; no network or API key."""
import contextlib
import io
import json
import tempfile
import unittest
import copy
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import fetch_news as cw


def http_error(code, message, details=None):
    body = json.dumps({'error': {'message': message, 'details': details or []}}).encode()
    return HTTPError('https://example.invalid/model', code, 'test error', {}, io.BytesIO(body))


def success():
    return io.BytesIO(json.dumps({'candidates': [{'content': {'parts': [{'text': '{"ok": true}'}]}}]}).encode())


class GeminiRegressionTests(unittest.TestCase):
    def setUp(self):
        cw.GEMINI_CACHE.clear()
        cw._GEMINI_CALL_TIMES.clear()
        cw._GEMINI_UNAVAILABLE_MODELS.clear()
        self.settings = patch.multiple(cw, GEMINI_API_KEY='test-key-never-log',
            GEMINI_MODEL='primary', GEMINI_MODEL_FALLBACKS=['alternate'],
            GEMINI_RPM_LIMIT=1000, GEMINI_RETRY_ON_429=1,
            GEMINI_RETRY_TRANSIENT=1, GEMINI_DISABLE_AFTER_CONSECUTIVE_503=2,
            _GEMINI_DISABLED_THIS_RUN=False, _GEMINI_CONSECUTIVE_503=0,
            _GEMINI_REVIEW_DEADLINE=None)
        self.settings.start()
        self.addCleanup(self.settings.stop)

    def test_depleted_credits_stop_after_one_request_without_sleep(self):
        output = io.StringIO()
        with patch('urllib.request.urlopen', side_effect=http_error(429, 'Your prepayment credits are depleted.')) as request, patch('time.sleep') as sleep, contextlib.redirect_stdout(output):
            for number in range(34):
                self.assertIsNone(cw.call_gemini_json(str(number), 'article'))
        self.assertEqual(request.call_count, 1)
        sleep.assert_not_called()
        self.assertNotIn(cw.GEMINI_API_KEY, output.getvalue())

    def test_retired_primary_allows_configured_alternate(self):
        with patch('urllib.request.urlopen', side_effect=[http_error(404, 'Model no longer available'), success()]) as request:
            self.assertEqual(cw.call_gemini_json('one', 'article'), {'ok': True})
        self.assertEqual(request.call_count, 2)
        self.assertFalse(cw._GEMINI_DISABLED_THIS_RUN)
        self.assertEqual(cw._gemini_models(), ['alternate'])
        for call in request.call_args_list:
            req = call.args[0]
            self.assertNotIn(cw.GEMINI_API_KEY, req.full_url)
            self.assertEqual(req.get_header('X-goog-api-key'), cw.GEMINI_API_KEY)

    def test_transient_429_retries_once_and_recovers(self):
        with patch('urllib.request.urlopen', side_effect=[http_error(429, 'Rate limit'), success()]) as request, patch('time.sleep') as sleep:
            self.assertEqual(cw.call_gemini_json('one', 'article'), {'ok': True})
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once()

    def test_persistent_429_does_not_cycle_models_or_articles(self):
        with patch('urllib.request.urlopen', side_effect=lambda *a, **k: (_ for _ in ()).throw(http_error(429, 'Rate limit'))) as request, patch('time.sleep'):
            for number in range(34):
                self.assertIsNone(cw.call_gemini_json(str(number), 'article'))
        self.assertEqual(request.call_count, 2)

    def test_daily_quota_stops_without_retry(self):
        details = [{'violations': [{'quotaId': 'GenerateRequestsPerDay', 'quotaValue': '20'}]}]
        with patch('urllib.request.urlopen', side_effect=http_error(429, 'Quota exceeded', details)) as request, patch('time.sleep') as sleep:
            self.assertIsNone(cw.call_gemini_json('one', 'article'))
        self.assertEqual(request.call_count, 1)
        sleep.assert_not_called()

    def test_access_denied_stops_without_trying_other_models(self):
        with patch('urllib.request.urlopen', side_effect=http_error(403, 'Denied')) as request:
            self.assertIsNone(cw.call_gemini_json('one', 'article'))
            self.assertIsNone(cw.call_gemini_json('two', 'article'))
        self.assertEqual(request.call_count, 1)

    def test_retry_respects_remaining_review_budget(self):
        with patch.object(cw, '_GEMINI_REVIEW_DEADLINE', 105), patch('time.monotonic', return_value=100), patch('urllib.request.urlopen', side_effect=http_error(429, 'Rate limit')) as request, patch('time.sleep') as sleep:
            self.assertIsNone(cw.call_gemini_json('one', 'article'))
        self.assertEqual(request.call_count, 1)
        sleep.assert_not_called()

    def test_503_breaker_stops_repeated_review_calls(self):
        with patch('urllib.request.urlopen', side_effect=lambda *a, **k: (_ for _ in ()).throw(http_error(503, 'Unavailable'))) as request, patch('time.sleep'):
            for number in range(5):
                self.assertIsNone(cw.call_gemini_json(str(number), 'article'))
        self.assertEqual(request.call_count, 2)


class PreservationTests(unittest.TestCase):
    def test_offline_generation_keeps_bilingual_articles_and_shared_styles(self):
        from validate_site import PageParser
        from xml.etree import ElementTree
        original = json.loads(cw.POSTS_JSON.read_text(encoding='utf-8'))[:2]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            replacements = {
                'POSTS_JSON': root / 'posts.json', 'POSTS_JS': root / 'posts.js',
                'POSTS_INDEX_JSON': root / 'assets/data/posts-index.json',
                'ARCHIVE_POSTS_JSON': root / 'all_posts.json',
                'FEED_XML': root / 'feed.xml', 'SITEMAP_XML': root / 'sitemap.xml',
                'ROBOTS_TXT': root / 'robots.txt',
                'PREVIEW_DIR': root / 'noticia', 'PREVIEW_EN_DIR': root / 'en/news',
                'RUN_NEW_SLUGS_JSON': root / '.cosmos-new-slugs.json',
            }
            with patch.multiple(cw, **replacements), patch.object(cw, 'enrich_posts_media'), patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected network request')) as network:
                cw.save_posts([cw.mark_preserve_content(copy.deepcopy(post)) for post in original])
            network.assert_not_called()
            generated = json.loads((root / 'posts.json').read_text())
            self.assertEqual([p['slug'] for p in generated], [p['slug'] for p in original])
            for post, before in zip(generated, original):
                for language, prefix in [('pt', 'noticia'), ('en', 'en/news')]:
                    self.assertEqual(post[f'body_{language}'], before[f'body_{language}'])
                    raw = (root / prefix / post['slug'] / 'index.html').read_text()
                    parser = PageParser()
                    parser.feed(raw)
                    css = [ref for ref in parser.refs if '/assets/css/article-base-' in ref]
                    self.assertEqual(len(css), 1)
                    self.assertTrue((cw.ROOT / css[0].lstrip('/')).is_file())
                    for schema in parser.json_ld:
                        json.loads(schema)
            ElementTree.parse(root / 'feed.xml')
            ElementTree.parse(root / 'sitemap.xml')

    def test_feed_outage_preserves_existing_edition(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'posts.json'
            original = '[{"slug":"existing","title":"Preserved article"}]'
            path.write_text(original)
            with patch.object(cw, 'POSTS_JSON', path), patch.object(cw, 'load_all_items', return_value=[]), patch.object(cw, 'dedupe_and_rank', return_value=[]), patch.object(cw, 'write_run_new_slugs') as marker, patch.object(cw, 'save_posts') as save, patch.dict('os.environ', {'COSMOS_REBUILD_FROM_EXISTING': ''}):
                cw.main()
            self.assertEqual(path.read_text(), original)
            save.assert_not_called()
            marker.assert_called_once_with([])

    def test_public_cards_preserve_bilingual_text_and_links(self):
        posts = json.loads(cw.POSTS_JSON.read_text(encoding='utf-8'))
        cards = cw.summary_index_posts(posts)
        self.assertEqual(len(cards), len(posts))
        for original, card in zip(posts, cards):
            for field in ['title', 'excerpt', 'read', 'date', 'keywords']:
                for language in ['pt', 'en']:
                    key = f'{field}_{language}'
                    self.assertEqual(card.get(key, card.get(field)), original.get(key, original.get(field)))
            self.assertEqual(card['shareUrl_pt'], original['shareUrl_pt'])
            self.assertEqual(card['shareUrl_en'], original['shareUrl_en'])
            self.assertFalse({'body', 'body_pt', 'body_en', 'inline_images'} & card.keys())


if __name__ == '__main__':
    unittest.main()
