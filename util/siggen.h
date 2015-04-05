#ifndef __SIGGEN_H__
#define __SIGGEN_H__

#include "core/parameter.h"

enum osc_type {
    OSC_SINE,
    OSC_TRIANGLE,
    OSC_SAWTOOTH,
    OSC_SQUARE,
};

extern quant_labels_t osc_quant_labels;
float osc_fn_gen(enum osc_type type, float phase);

#endif
