#!/usr/bin/env python3
"""Execute one lettering item and persist/report progress around the operation."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


def validate_svg(path):
    r = ET.parse(path).getroot()
    assert r.findall('.//{http://www.w3.org/2000/svg}path'), 'No vector paths'
    assert not r.findall('.//{http://www.w3.org/2000/svg}image'), 'Embedded bitmap'
    assert r.get('viewBox'), 'Missing viewBox'


def execute(args):
    p = args.manifest.resolve()
    m = json.loads(p.read_text(encoding="utf-8"))
    item = next(i for i in m['items'] if i['index'] == args.index)
    settings = m['settings']
    def save():
        # Atomic replacement makes interruption less likely to corrupt task IDs.
        temp = p.with_suffix('.json.tmp')
        temp.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(p)
    def cli(arguments, suffix):
        r = subprocess.run([args.cli] + arguments, capture_output=True, text=True)
        raw = p.parent / f"{args.index:03}_{suffix}.json"
        raw.write_text(r.stdout, encoding="utf-8")
        try:
            data = json.loads(r.stdout)
        except ValueError:
            raise RuntimeError('Ambiguous CLI response; inspect task history before any resubmission')
        return data
    stem = f"{item['index']:03}_" + re.sub(r'[/\\\x00-\x1f]', '_', item['title'])[:100]
    if args.action == 'submit':
        if item['stage'] != 'pending':
            raise RuntimeError('Only pending items may submit; recover/query an existing task instead')
        if item.get('variants', 1) != 1:
            raise RuntimeError('This runner supports one image per title; handle variant selection separately')
        item['stage'] = 'submitting'; save()
        data = cli(['image2image', '--images='+settings['reference'], '--prompt='+item['prompt'],
                    '--ratio='+settings['ratio'], '--resolution_type='+settings['resolution'],
                    '--model_version='+settings['model'], '--generate_num=1', '--poll=0'], 'submit')
        item.setdefault('attempts', []).append(data)
        if data.get('submit_id'):
            item['submit_id'] = data['submit_id']; item['stage'] = 'submitted'
        else:
            item['error'] = 'No accepted task ID; inspect saved response and task history'
        save()
    elif args.action == 'download':
        if not item.get('submit_id') or item['stage'] == 'completed':
            raise RuntimeError('Needs an accepted, unfinished task')
        dest = p.parent / f"{args.index:03}_download"
        dest.mkdir(exist_ok=True)
        data = cli(['query_result', '--submit_id='+item['submit_id'], '--download_dir='+str(dest)], 'query')
        status = data.get('gen_status')
        if status == 'success':
            images = data.get('result_json', {}).get('images', [])
            if len(images) != 1 or not Path(images[0].get('path', '')).is_file():
                raise RuntimeError('Generation succeeded but no single downloaded image; query download again')
            item['source'] = images[0]['path']; item['stage'] = 'downloaded'
        elif status == 'fail':
            item['stage'] = 'failed'; item['error'] = data.get('fail_reason', 'Generation failed')
        else:
            item['last_query'] = data
        save()
    elif args.action == 'trace':
        if item['stage'] != 'downloaded':
            raise RuntimeError('Download first')
        from PIL import Image, ImageOps
        import vtracer
        im = Image.open(item['source']).convert('RGB')
        png, svg = p.parent/(stem+'.png'), p.parent/(stem+'.svg')
        im.save(png)
        binary = p.parent / f'{args.index:03}_trace-input.png'
        ImageOps.grayscale(im).point(lambda v: 0 if v < 128 else 255).convert('RGB').save(binary)
        vtracer.convert_image_to_svg_py(str(binary), str(svg), colormode='binary', mode='spline',
                                       filter_speckle=4, corner_threshold=60, length_threshold=4.0, path_precision=3)
        tree = ET.parse(svg); tree.getroot().set('viewBox', f'0 0 {im.width} {im.height}')
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        tree.write(svg, encoding='utf-8', xml_declaration=True)
        validate_svg(svg)
        item.update(png=str(png), svg=str(svg), stage='needs_review'); save()
    elif args.action == 'approve':
        if item['stage'] != 'needs_review' or not args.reviewed:
            raise RuntimeError('Requires --reviewed after text and SVG render inspection')
        validate_svg(item['svg'])
        item['stage'] = 'completed'
        item['validation'] = {'xml_valid': True, 'render_checked': True, 'text_checked': True}
        save()
    print(json.dumps({'index':item['index'], 'stage':item['stage']}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--host', required=True, choices=['codex','kiro'])
    parser.add_argument('--index', required=True, type=int)
    parser.add_argument('--action', required=True, choices=['submit','download','trace','approve'])
    parser.add_argument('--cli', default=shutil.which('dreamina') or str(Path.home()/'.local/bin/dreamina'))
    parser.add_argument('--reviewed', action='store_true')
    args = parser.parse_args()
    # One manifest has one writer at a time; hosts should run items sequentially.
    try:
        execute(args)
    finally:
        pass


if __name__ == '__main__':
    main()
