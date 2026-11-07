# -*- coding: utf-8 -*-
"""Offline checks of the PvE patch of mpfever_ai.lua through lupa: the styles on top of the levels, and a computer company out of
the game (bankrupt in PvE) never started again.

Run: python tests/test_pve_ai.py (or with another content folder as its argument)
"""
import os
import sys

try:
    import lupa.lua52 as lua52
except ImportError:
    print("lupa is not installed (pip install lupa)")
    sys.exit(1)

here = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mod", "mpfever_1", "content")
failures = []


def check(cond, what):
    print(("  ok    " if cond else "  FAIL  ") + what)
    if not cond:
        failures.append(what)


def module(env):
    L = lua52.LuaRuntime(unpack_returned_tuples=True)
    L.execute('ENVOVR = {}; do local og = os.getenv; os.getenv = function(k) local v = ENVOVR[k] if v ~= nil then return v end return og(k) end end')
    for k, v in env.items():
        L.execute('ENVOVR["%s"] = "%s"' % (k, v))
    M = L.execute(open(os.path.join(here, "mpfever_ai.lua"), encoding="utf-8").read())
    L.globals().M = M
    run = L.eval("function(code) local f = assert(load(code)) return f() end")
    return L, run


print("styles")
L, run = module({"MPFEVER_PVE": "1", "MPFEVER_PVE_STYLE": "1:aggressive, 2:Conservative,3:balanced"})
run('LV2 = { name = "normal", tick = 60, reserve = 400000, freeCash = 2000000, settle = 360000, pause = 600, bootstrap = 2, maxUnproven = 1, addMargin = 1.15, giveUp = 0.5, compete = false }')
check(run('return M.pveStyleOf(1)') == "aggressive", "company 1 is aggressive")
check(run('return M.pveStyleOf(2)') == "conservative", "company 2 is conservative (any case)")
check(run('return M.pveStyleOf(3)') is None, "company 3 balanced: the level as it is")
check(run('return M.pveStyleOf(4)') is None, "company 4 not named: the level as it is")
check(run('local a = M.pveStyled(LV2, 1) return a.reserve == 240000 and a.freeCash == 1000000 and a.settle == 180000 and a.pause == 300 and a.bootstrap == 3 and a.maxUnproven == 2 and a.compete == true and math.abs(a.addMargin - 1.1) < 1e-9 and a.name == "normal" and a.tick == 60') is True,
      "aggressive: less money kept back, shorter waits, more first lines, competes; name and pace kept")
check(run('local c = M.pveStyled(LV2, 2) return c.reserve == 600000 and c.bootstrap == 1 and c.maxUnproven == 1 and c.compete == false and math.abs(c.addMargin - 1.25) < 1e-9 and c.giveUp <= 0.95') is True,
      "conservative: more money kept back, fewer first lines, does not compete")
check(run('local b = M.pveStyled(LV2, 3) return b == LV2') is True, "balanced: the level itself")
check(run('M.pveStyled(LV2, 1); return LV2.reserve == 400000 and LV2.compete == false') is True, "the level itself is never changed")

L, run = module({"MPFEVER_PVE_STYLE": "1:aggressive"})
check(run('return M.pveStyleOf(1)') is None, "no style while PvE is off")

print("a computer company out of the game")
for out in (True, False):
    L, run = module({"MPFEVER_PVE": "1"})
    run('''
LOGS = {}
G = { frames = 0, cmode = "separate", connected = true, session = { started = true }, myCo = 1, coAi = "1:5:2:-1",
      co = { list = {}, pveOut = %s } }
E = { G = G, C = { ROLE = "host", IO = nil, PALETTE = {} }, CO = { byKey = function() return nil end, PALETTE = { 1, 2, 3, 4, 5, 6, 7, 8 } },
      log = function(s) LOGS[#LOGS + 1] = s end, gameTime = function() return 0 end }
''' % ('{ ["ai:1"] = true }' if out else '{}'))
    run('M.tick(E, {})')            # (its first look: not before the session's first minute)
    run('G.frames = 700')
    ok = run('local ok, err = pcall(M.tick, E, {}) return ok')
    said = run('for _, s in ipairs(LOGS) do if s:find("[PvE] bankrupt", 1, true) then return true end end return false')
    if out:
        check(ok is True and said is True, "out of the game: its look ends there, never starts a company again")
    else:
        check(said is False, "still in the game: its look goes on (into the rest of the module)")

if failures:
    print(f"FAIL: {len(failures)} check(s)")
    sys.exit(1)
print("PASS")
