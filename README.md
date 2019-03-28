# NanoUpTools
A lightweight Tools for analyzing NanoAOD format, with uproot for reading file
and rootpy for histogram. The code structure is designed to follow the NanoAOD-tools on
purpose.

### Issues:
1. After the end of iterate() with catching the stopIteration, the rootpy
   crash when creating a new Hist()

### Tips

*Matching*

```
x = jet.cross(genjet)
matched = x.i0.delta_r(x.i1) < 0.4
response = x[matched].i0.pt / x[matched].i1.pt
```
