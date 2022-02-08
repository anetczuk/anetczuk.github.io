---
title: Performance of Python binding libraries

summary: Comparison of performance of ctypes, cffi and swig libraries.
---

I've recently made two projects involving call of C/C++ libraries from Python, 
namely technique called *Python bindings*. First project, [*dk-mage*](https://github.com/anetczuk/dk-mage), 
uses *Swig* bindings generator. The other project, [*ReverseCRC*](https://github.com/anetczuk/ReverseCRC), 
demonstrates use of following binding libraries: *ctypes*, *CFFI* and *Swig*.

Use case for first project is just to use functionality provided by C++ library.

Purpose of binding in second project is to improve CPU performance by providing 
C implementation of algorithms. Unsurprisingly, each library have different performance overhead.


## Table of Contents
1. [Task](#task)
2. [Measurements](#measurements)
3. [Ease of use](#ease-of-use)
4. [Conclusion](#conclusion)
5. [Components versions](#components-versions)
6. [References](#references)


## Task

Main purpose of *ReverseCRC* project is to find *CRC key* based on given data 
frames (raw data and resulting CRC values). Solution for reversing CRC consists 
of tuple of values: polynomial, registry initial value and result xor value. Then 
search space is following: `2 ^ (3 * bit_length(CRC))`. 

Among others, application operates in *BACKWARD* mode. In order to solve CRC 
problem, in first step it calculates potential candidates for the solution (pairs 
of *init* and *xor* values) using first data frame and then uses it as input to 
reduced exhaustive search against rest of data frames. This approach reduces 
search space by one dimension.


## Measurements

Each plot consists of 4 lines corresponding to different binding:
- *cffi* is *CFFI* implementation,
- *ctypes* is *ctypes* implementation,
- *swigoo* is *Swig* binding using object-oriented flavored wrappers,
- *swigraw* is *Swig* binding using simple mapping.

Moreover, because of nature of project, there are two kinds of measurements taken:
- *direct* where data frames are converted during every call to C library,
- *cached* where data frames are converted only once and cached for consecutive calls.

Each measurment is taken against following input:
- CRC size: 16 bits
- data frame/row size: 8, 16, 24 and 32 bytes respectively
- data frames number: 8
- polynomial under test: 0x1335D

Search space is following: `2^(3*16) = 2^48 ~= 281 474 980 000`. For this reason 
one polynomial values was preselected.

As base for measurments serves *BACKWARD* task. 

Following image shows performance comparison in *direct* mode:
[![Performance against BACKWARD task](/img/post/2022-02-06/BACKWARD_direct_db-8_16_24_32-_crc16_dr8_dgFF_sub-small.png "Performance against BACKWARD task")](/img/post/2022-02-06/BACKWARD_direct_db-8_16_24_32-_crc16_dr8_dgFF_sub.png)

Numbers:
```
data_size      cffi    ctypes    swigoo   swigraw
        8  0.669771  1.200688  3.040263  1.263048
       16  0.841836  1.689529  4.114837  1.782414
       24  1.000750  2.192260  5.087483  2.290749
       32  1.187108  2.697481  6.078609  2.828679
```

Next image shows presents the same measurement, but taken in *cached* mode:
[![Performance against BACKWARD task](/img/post/2022-02-06/BACKWARD_cached_db-8_16_24_32-_crc16_dr8_dgFF_sub-small.png "Performance against BACKWARD task")](/img/post/2022-02-06/BACKWARD_cached_db-8_16_24_32-_crc16_dr8_dgFF_sub.png)

Numbers:
```
data_size      cffi    ctypes    swigoo   swigraw
        8  0.506151  0.594125  0.647912  0.548720
       16  0.552889  0.636546  0.696747  0.594223
       24  0.600424  0.685254  0.742332  0.642770
       32  0.643498  0.738896  0.783708  0.691665
```

As it can be clearly seen, a lot of CPU cycles goes to conversion of data frames 
to raw C arrays. When data is cached, then there is only constant time difference 
between libraries resulting from different *intermediate* layers. The fastest one 
is *cffi* implementation, because it uses *intermediate* layer generated and compiled 
in C. The slowest one is *swigoo* implementation. It's *intermediate* layer consists 
of Python wrapper and C wrapper at the same time. It gives flexibility in cost of 
aditional CPU cycles.


## Ease of use

Each of libraries under consideration have it's pros and cons. 

*ctypes* is simplest one -- do not require additional building steps. One have to 
write *intermediate* layer by himself. In case of simple C functions it is straightforward, 
but difficulty arises in case of structs and multitude of functions to export. 

*cffi* prepares *intermediate* layer based on provided C declarations. It compiles 
it into C wrapper ready for import. It automatically converts lists and arrays between 
languages (at least in case of numeric containers).

*swig* follows the same path -- it generates required bindings based on C/C++ declarations. 
Aside of the declaration it requires *interface* files describing generation rules. 
*Swig* is easy to use in case of simple code transformations (*dk-mage* is good 
example), but it can be not as obvious in case of fancy things like adding auto 
memory management to C library (see *swigoo* implementation).


## Conclusion

It seems that in case of *non trivial* C++ projects *swig* is easiest to use. In 
case of macro-generated C code there is no help in *swig* nor in *cffi*. For both 
of them macros have to be unrolled in order to be feed to the generators. If performance 
is crucial, then *cffi* is the choice.


## Components versions

Given analysis was performed based on following versions and revisions:
- *ReverseCRC* revision `bce5fa62744dea0f71762d98f6a78c77e648f5f9`
- *dk-mage* revision `8f15fc6be1cf17488d9ded6645620ab602f85bbe`
- *ctypes* version from Python 2.7.18
- *cffi* version 1.15.0
- *swig* version 3.0.12


## References

- [Overview of Python's bindings](https://realpython.com/python-bindings-overview/)
- [ctypes](https://docs.python.org/3/library/ctypes.html) library
- [CFFI](https://cffi.readthedocs.io/en/latest/) library
- [Swig](http://www.swig.org/) library
- [ReverseCRC](https://github.com/anetczuk/ReverseCRC)
- [dk-mage](https://github.com/anetczuk/dk-mage)
