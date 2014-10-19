import lightstrip

def composite(frames):
    output_strip=[]
    for i in range(lightstrip.STRIP_LENGTH):
        o_r=0
        o_g=0
        o_b=0
        for (f,f_a) in frames[::-1]: # 1st frame should be 'on top'
            (r,g,b,a)=f[i]
            a*=f_a
            o_r=o_r*(1-a)+r*a
            o_g=o_g*(1-a)+g*a
            o_b=o_b*(1-a)+b*a

        output_strip.append((o_r,o_g,o_b))

    return output_strip
