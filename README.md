ISO base media file format parser
=================================

isomedia is a library used to parse ISO base media file formats (https://en.wikipedia.org/wiki/ISO_base_media_file_format). In particular, it offers simple extensions to parse MOV, MP4 and 3GP video file formats that derive from the ISO base media file format.

Usage
-----

```python
import isomedia

f = open('selfie_vine.mp4', 'rb')
isofile = isomedia.load(f)

moov = [atom for atom in isofile.children if atom.type() == 'moov']
```
