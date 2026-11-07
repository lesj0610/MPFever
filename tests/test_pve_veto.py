# -*- coding: utf-8 -*-
"""Offline checks of the PvE demolition rules (G.pveVeto, the bridge patch) through lupa, with a mocked tool proposal.

Run: python tests/test_pve_veto.py
"""
import os
import sys

try:
    import lupa.lua52 as lua52
except ImportError:
    print("lupa is not installed (pip install lupa)")
    sys.exit(1)

# (the rules' definition, read from the bridge itself: from "G.pveVeto = function" to the function after it)
bridge = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mod", "mpfever_1", "content", "mpfever_bridge.script.lua"),
              encoding="utf-8").read().replace("\r\n", "\n")
src = bridge[bridge.index("G.pveVeto = function"):bridge.index("\nlocal function guiHandleEvent(")]
failures = []


def check(cond, what):
    print(("  ok    " if cond else "  FAIL  ") + what)
    if not cond:
        failures.append(what)


MOCK = r'''
ENVOVR = {}
do local og = os.getenv; os.getenv = function(k) local v = ENVOVR[k] if v ~= nil then return v end return og(k) end end
G = {}
LOGS = {}
function log(s) LOGS[#LOGS + 1] = s end
-- the world: 10 a town building's construction, 11 an industry, 12 the player's station, 20 a street of no company,
-- 21 the player's street (owner 100), 22 a track of no company
COMP = {
  [10] = { con = { townBuildings = { 1 }, simBuildings = {}, fileName = "town/house.con" } },
  [11] = { con = { townBuildings = {}, simBuildings = { 1 }, fileName = "industry/coal_mine.con" } },
  [12] = { con = { townBuildings = {}, simBuildings = {}, fileName = "station/rail/modular.con" }, po = { player = 100 } },
  [20] = { be = {}, bes = {} },
  [21] = { be = {}, bes = {}, po = { player = 100 } },
  [22] = { be = {} },
}
api = { type = { ComponentType = { TOWN_BUILDING = "tb", CONSTRUCTION = "con", INDUSTRY = "ind", BASE_EDGE_STREET = "bes", PLAYER_OWNED = "po" } },
  engine = { getComponent = function(e, ct) local c = COMP[e] return c and c[ct] or nil end } }
function P(toRemove, removedSegs, gathered, critical)
  local rs = {}
  for i, e in ipairs(removedSegs or {}) do rs[i] = { entity = e } end
  local be = {}
  for i = 1, (gathered or 0) do be[i] = 1000 + i end
  return { { toRemove = toRemove or {}, proposal = { removedSegments = rs } }, { collisionInfo = { buildingEntities = be }, errorState = { critical = critical == true } } }
end
function why(r) if r == nil then return nil end for k in pairs(r.errorMessages) do return k end end
'''


def world(env):
    L = lua52.LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCK)
    for k, v in env.items():
        L.execute('ENVOVR["%s"] = "%s"' % (k, v))
    L.execute(src)
    return L.eval("function(code) local f = assert(load(code)) return f() end")


print("PvE off: nothing turned down")
run = world({})
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10 }, { 20 })))') is None, "a town building and a town street: allowed")

print("PvE on, the defaults: everything protected")
run = world({"MPFEVER_PVE": "1"})
check("마을 건물" in (run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10 })))') or ""), "the bulldozer on a town building: turned down")
check("마을 건물" in (run('return why(G.pveVeto("streetBuilder", "builder.proposalCreate", P({}, {}, 3)))') or ""), "a street through 3 houses: turned down")
check("산업" in (run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 11 })))') or ""), "the bulldozer on an industry: turned down")
check("도로" in (run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({}, { 20 })))') or ""), "the bulldozer on a street of no company: turned down")
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({}, { 21 })))') is None, "the bulldozer on the player's own street: allowed")
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({}, { 22 })))') is None, "the bulldozer on a track: allowed")
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 12 })))') is None, "the bulldozer on the player's own station: allowed")
check(run('return why(G.pveVeto("streetBuilder", "builder.proposalCreate", P({}, { 20 })))') is None, "upgrading a town street (street tool): allowed")
check(run('return why(G.pveVeto("bulldozer", "builder.proposalApply", P({ 10 })))') is None, "other events: no answer")
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10 }, {}, 0, true)))') is None, "a proposal the game already refuses: no answer")
check(run('local r = G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10 })) return r.skipRender == false') is True, "the tool still shows its proposal")

print("PvE on, all allowed")
run = world({"MPFEVER_PVE": "1", "MPFEVER_PVE_DEMOLISH_TOWN": "1", "MPFEVER_PVE_DEMOLISH_INDUSTRY": "1", "MPFEVER_PVE_DEMOLISH_ROAD": "1"})
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10, 11 }, { 20 }, 2)))') is None, "everything allowed")

print("PvE on, town buildings allowed only")
run = world({"MPFEVER_PVE": "1", "MPFEVER_PVE_DEMOLISH_TOWN": "1"})
check(run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10 }, {}, 1)))') is None, "a town building: allowed")
check("산업" in (run('return why(G.pveVeto("bulldozer", "builder.proposalCreate", P({ 10, 11 })))') or ""), "an industry with it: still turned down")

if failures:
    print(f"FAIL: {len(failures)} check(s)")
    sys.exit(1)
print("PASS")
