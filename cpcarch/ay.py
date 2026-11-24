"""A simplified AY-3-8912 renderer: a stream of register sets (e.g. 100 per second, one per call of a game's
sound driver) becomes stereo audio.

CPC AY clock: 1 MHz. A tone channel with period P sounds at 62 500 / P Hz (square wave); the noise generator is a
17-bit shift register stepped 62 500 / N times per second. Volume (0-15) follows the chip's logarithmic scale.
The hardware envelope (registers 11-13) is NOT modelled: add it if your game uses it.
Output: channel A left, B centre, C right, like the CPC stereo socket.
"""
import numpy as np

RATE = 44100
LEVELS = np.array([0.0, 0.00999, 0.01445, 0.02105, 0.03070, 0.04558, 0.06450, 0.10750,
                   0.12659, 0.20499, 0.29221, 0.37284, 0.49253, 0.63532, 0.80558, 1.0])


def _noise():
    x, s = 1, np.empty(131071, dtype=np.uint8)
    for i in range(131071):
        b = (x ^ (x >> 3)) & 1
        x = (x >> 1) | (b << 16)
        s[i] = x & 1
    return s


NOISE = _noise()


def synthesize(registers, hz=100):
    """registers: sequence of 11-byte sets (tone periods A, B, C, noise period, mixer, volumes A, B, C), `hz` per
    second. Returns a (samples, 2) float array normalised to 0.9."""
    per = RATE / hz
    n = int(len(registers) * per)
    out = np.zeros((n, 3))
    phase = np.zeros(3)
    pn = 0.0
    for k, r in enumerate(registers):
        i0, i1 = int(k * per), int((k + 1) * per)
        t = np.arange(1, i1 - i0 + 1)
        nb = max(1, r[6] & 0x1F)
        idx = ((pn + t * (62500 / nb) / RATE).astype(np.int64)) % len(NOISE)
        noise = NOISE[idx]
        pn += (i1 - i0) * (62500 / nb) / RATE
        for v in range(3):
            p = max(1, r[2 * v] | (r[2 * v + 1] & 0x0F) << 8)
            ph = phase[v] + t * (62500 / p) / RATE
            tone = ((ph % 1.0) < 0.5).astype(np.uint8)
            phase[v] = ph[-1] % 1.0
            tone_off = r[7] >> v & 1
            noise_off = r[7] >> (v + 3) & 1
            sig = (tone | tone_off) & (noise | noise_off)
            out[i0:i1, v] = sig * LEVELS[r[8 + v] & 0x0F]
    left = out[:, 0] + 0.5 * out[:, 1]
    right = out[:, 2] + 0.5 * out[:, 1]
    st = np.stack([left, right], axis=1)
    from scipy.signal import lfilter                       # DC removal: 20 Hz high-pass
    a = np.exp(-2 * np.pi * 20 / RATE)
    y = lfilter([1, -1], [1, -a], st, axis=0)
    y /= max(1e-9, np.abs(y).max()) / 0.9
    return y


def write_wav(path, y):
    import wave
    w = wave.open(path, 'wb')
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes((y * 32767).astype('<i2').tobytes())
    w.close()


# French names used by the Antiriad scripts
synthese, ecrire_wav = synthesize, write_wav
