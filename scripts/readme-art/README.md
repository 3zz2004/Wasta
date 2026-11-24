# README art

The banner and terminal demo in the main README are generated from code, not
drawn by hand. GitHub shows README images in a sandbox where web fonts never
load, so every glyph is converted to an outline. Arabic is shaped with
HarfBuzz first, so letters join the way they should.

```bash
sh fetch-fonts.sh
pip install -r requirements.txt
python banner.py ../../assets
python demo.py ../../assets
```

The examples in the banner are also test cases in `spec/`, so they can't drift
from what the library actually returns.
