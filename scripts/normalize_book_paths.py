#!/usr/bin/env python3
"""Migrate the two legacy Livro routes without overwriting canonical content.

Also handles an upload made over the old checkout. GitHub runners are case
sensitive; Windows may need the intermediate directory rename below.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    upper = ROOT / 'Livro'
    lower = ROOT / 'livro'
    if not upper.exists():
        return
    if lower.exists() and upper.samefile(lower):
        actual = next((p for p in ROOT.iterdir() if p.name == 'Livro'), None)
        if actual:
            temporary = ROOT / '__cosmos_book_case_migration__'
            if temporary.exists():
                raise SystemExit('Diretório temporário de migração já existe; nenhuma alteração realizada.')
            upper.rename(temporary)
            temporary.rename(lower)
        return
    known = {'index.html', 'vortice-maligno/checklist/index.html'}
    files = [p for p in upper.rglob('*') if p.is_file()]
    unknown = [str(p.relative_to(upper)) for p in files if p.relative_to(upper).as_posix() not in known]
    if unknown:
        raise SystemExit(f'Livro contém arquivos não reconhecidos; revise antes de migrar: {unknown}')
    for source in files:
        target = lower / source.relative_to(upper)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif source.read_bytes() != target.read_bytes():
            raise SystemExit(f'Conteúdos diferentes em {source} e {target}; nenhum arquivo legado foi removido.')
    for source in files:
        source.unlink()
    for directory in sorted((p for p in upper.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        directory.rmdir()
    upper.rmdir()
    print('Rotas legadas Livro normalizadas para livro.')


if __name__ == '__main__':
    main()
