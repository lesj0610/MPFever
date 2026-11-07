# -*- coding: utf-8 -*-
"""Offline checks of the PvE patch (mpfever_eco.lua + mpfever_co.lua patched), with a mocked game API through lupa (Lua 5.2), the
way MPFever's own tests/test_ai_bankrupt.py does.

Run: python tests/test_pve.py (or with another content folder as its argument)

Cases:
  PvE off      MPFever as before: a computer company never goes bankrupt, a player does
  PvE on       a player is never counted in debt nor goes bankrupt; a computer company goes bankrupt after the host's months, is
               marked out of the game (its key and its key without "@..."), its news carries the PvE text; the auction is MPFever's
               (default); the last computer company out: the player wins (once)
  PvE remove   no auction: its lines, vehicles, stations and depots removed, its tracks a moment later (E.tick), its roads kept
"""
import os
import sys

try:
    import lupa.lua52 as lua52
except ImportError:
    print("lupa is not installed (pip install lupa)")
    sys.exit(1)

here = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mod", "mpfever_1", "content")

MOCK = r'''
ENVOVR = {}
do
  local og = os.getenv
  os.getenv = function(k) local v = ENVOVR[k] if v ~= nil then return v end return og(k) end
end
TIME = 0
BAL = {}
OWN = {}
EDGE = {}          -- edge -> "track" | "street"
SENT = {}
RMLIST = nil       -- the segments given to makeSegmentsRemoveProposal
LINES = {}         -- player -> { lines }
VEH = {}           -- player -> { vehicles }
api = {
  type = { JournalEntry = { new = function() return { category = {} } end, Type = { OTHER = 1, ACQUISITION = 3 } }, Vec3f = { new = function() return {} end },
    ComponentType = { PLAYER_OWNED = "po", NAME = "name", BASE_EDGE = "be", BASE_EDGE_STREET = "bes", CONSTRUCTION = "con",
      TRANSPORT_VEHICLE = "tv", LINE = "line", STATION_GROUP = "sg" },
    SimpleProposal = { new = function() return { streetProposal = {} } end }, Context = { new = function() return {} end } },
  util = { getDefaultMonthDuration = function() return 1000 end },
  cmd = { sendCommand = function(c) SENT[#SENT + 1] = c end,
    makeJournalBookAssetCmd = function(ent, e) BAL[ent] = (BAL[ent] or 0) + e.amount return { kind = "book" } end,
    makeEntitySetPlayerCmd = function(e, p) OWN[e] = p return { kind = "owner", e = e, p = p } end,
    makeVehicleSellCmd = function(v) return { kind = "sell", v = v[1] } end,
    makeLineDestroyCmd = function(l) return { kind = "destroy", l = l } end,
    makeWorldBuildProposalCmd = function(p, ctx) return { kind = "build", p = p, player = ctx and ctx.player } end },
  engine = {
    getComponent = function(e, ct)
      if ct == "po" then return OWN[e] and { player = OWN[e] } or nil end
      if ct == "be" then return EDGE[e] and {} or nil end
      if ct == "bes" then return EDGE[e] == "street" and {} or nil end
      if ct == "tv" then for _, list in pairs(VEH) do for _, v in ipairs(list) do if v == e then return { line = -1 } end end end return nil end
      if ct == "line" then for _, list in pairs(LINES) do for _, l in ipairs(list) do if l == e then return { stops = {} } end end end return nil end
      return nil
    end,
    entityExists = function(e) return true end,
    forEachEntityWithComponent = function() error("no loop in the mock") end,
    util = { finance = { getPlayersBalance = function(p) return BAL[p] or 0 end },
      proposal = { makeSegmentsRemoveProposal = function(list) RMLIST = list return { kind = "removal" } end } },
    system = {
      lineSystem = { getLinesForPlayer = function(p) return LINES[p] or {} end },
      transportVehicleSystem = { getLineVehicles = function() return {} end, getVehiclesForPlayer = function(p) return VEH[p] or {} end } } },
}
R = {
  allEdges = function() local o = {} for e in pairs(EDGE) do o[#o + 1] = e end table.sort(o) return o end,
  entitiesWith = function() return {} end, ownerOf = function(e) return OWN[e] end, sgKey = function(s) return "sg" .. s end,
  withoutAssets = function(l) return l end }
LOG = {}
ENV = { log = function(s) LOG[#LOG + 1] = s end, R = R, STEP = 200, gameTime = function() return TIME end, journalCarrier = function() return 1 end }
'''

failures = []


def check(cond, what):
    print(("  ok    " if cond else "  FAIL  ") + what)
    if not cond:
        failures.append(what)


def world(env):
    L = lua52.LuaRuntime(unpack_returned_tuples=True)
    L.execute(MOCK)
    for k, v in env.items():
        L.execute('ENVOVR["%s"] = "%s"' % (k, v))
    CO = L.execute(open(os.path.join(here, "mpfever_co.lua"), encoding="utf-8").read())
    L.globals().CO = CO
    L.execute("ENV.CO = CO")
    E = L.execute(open(os.path.join(here, "mpfever_eco.lua"), encoding="utf-8").read())
    L.globals().E = E
    run = L.eval("function(code) local f = assert(load(code)) return f() end")
    # the host's company, a player (bob), two computer companies; ai:2 joined under a key made unique ("ai:2@3"); the host's
    # rules: bankrupt after 3 months in debt, the lobby's computer companies 1 and 2
    run('''
st = { co = CO.new("separate", 100, 0) }
CO.join(st.co, "host", "Host", true, "Host Co", "s1", 1)
local b = CO.join(st.co, "bob", "Bob", false, "Bob Co", "s2", 2); b.ent = 200
local a1 = CO.join(st.co, "ai:1", "Regional Transport", false, "Regional Transport", nil, 3); a1.ent = 300
local a2 = CO.join(st.co, "ai:2", "Valley Coaches", false, "Valley Coaches", nil, 4); a2.ent = 400
a2.key = "ai:2@3"
st.co.rules = { bankrupt = 3, ai = "1:5:2:-1,2:6:3:-1" }
-- ai:1 owns two lines with a vehicle each, a track, a street; ai:2 a track
LINES[300] = { 31, 32 }; VEH[300] = { 41, 42 }; OWN[31] = 300; OWN[32] = 300; OWN[41] = 300; OWN[42] = 300
EDGE[51] = "track"; OWN[51] = 300
EDGE[52] = "street"; OWN[52] = 300
EDGE[53] = "track"; OWN[53] = 400
EDGE[54] = "track"; OWN[54] = 200
TIME = 0; E.tick(st, ENV)
''')
    return L, run


def months(run, n, debt):
    for _ in range(n):
        run('TIME = TIME + 1000; E.tick(st, ENV); E.event(st, "co_month", { month = st.co.month, debt = { %s }, mpfFrom = "Host" }, ENV)' % debt)


def count_news(run, kind):
    return run('local n = 0 for _, x in ipairs(st.co.news or {}) do if x.kind == "%s" then n = n + 1 end end return n' % kind)


print("PvE off: MPFever as before")
L, run = world({})
check(run('return E.PVE') is False, "PvE is off without MPFEVER_PVE")
months(run, 3, "2, 3")
check(run('return CO.find(st.co, 2).gone') == "bankrupt", "bob's company goes bankrupt after 3 months")
check(run('return CO.find(st.co, 3).gone') is None, "the computer company does not")
check(run('return st.co.pveOut') is None, "nothing marked out")

print("PvE on, the auction (default)")
L, run = world({"MPFEVER_PVE": "1"})
check(run('return E.PVE and not E.PVE_REMOVE and not E.AI_NO_BANKRUPT') is True, "PvE on, auction, computer companies may go bankrupt")
months(run, 2, "2, 3")
check(run('return CO.find(st.co, 2).debt') is None, "bob is never counted in debt")
check(run('return CO.find(st.co, 3).debt') == 2, "the computer company counts 2 months")
months(run, 1, "2, 3")
check(run('return CO.find(st.co, 2).gone') is None, "bob never goes bankrupt")
check(run('return CO.find(st.co, 3).gone') == "bankrupt", "the computer company goes bankrupt after 3 months")
check(run('return st.co.auction ~= nil and st.co.auction.co == 3') is True, "its assets go to MPFever's auction")
check(run('return st.co.pveOut["ai:1"] == true') is True, "ai:1 is marked out of the game")
check(run('local t for _, x in ipairs(st.co.news) do if x.kind == "bankrupt" then t = x.pveText end end return t') is not None,
      "its bankruptcy news carries the PvE text")
check(count_news(run, "pve_win") == 0, "no victory while ai:2 plays")
run('E.finishAuction(st, ENV)')
months(run, 30, "2, 4")
check(run('return CO.find(st.co, 4).gone') == "bankrupt", "the second computer company goes bankrupt too")
check(run('return st.co.pveOut["ai:2"] == true and st.co.pveOut["ai:2@3"] == true') is True, "ai:2 is marked out, under both keys")
check(count_news(run, "pve_win") == 1 and run('return st.co.pveWon') is True, "the player wins once")
run('E.finishAuction(st, ENV)')
run('E.pveCheckWin(st, ENV)')
check(count_news(run, "pve_win") == 1, "the victory is told once only")
check(run('return CO.find(st.co, 2).gone') is None and run('return CO.find(st.co, 2).debt') is None, "bob is still playing, never in debt")

print("PvE on, removal at once")
L, run = world({"MPFEVER_PVE": "1", "MPFEVER_PVE_REMOVE": "1"})
check(run('return E.PVE_REMOVE') is True, "removal at once is on")
months(run, 3, "3")
check(run('return CO.find(st.co, 3).gone') == "bankrupt", "the computer company goes bankrupt")
check(run('return st.co.auction') is None, "no auction")
sold = run('local n = 0 for _, c in ipairs(SENT) do if c.kind == "sell" then n = n + 1 end end return n')
gone = run('local n = 0 for _, c in ipairs(SENT) do if c.kind == "destroy" then n = n + 1 end end return n')
check(sold == 2 and gone == 2, f"its 2 vehicles sold and its 2 lines taken away (sold {sold}, lines {gone})")
check(run('return #st.co.pveJobs') == 1, "its tracks wait for a moment")
check(count_news(run, "pve_removed") == 1, "the removal is told")
run('TIME = TIME + 1000; E.tick(st, ENV)')
check(run('return RMLIST') is None, "not yet after 1 s")
run('TIME = TIME + 2500; E.tick(st, ENV)')
check(run('return RMLIST ~= nil and #RMLIST == 1 and RMLIST[1] == 51') is True, "then its one track (51) is removed, not its street nor the others' tracks")
check(run('return #st.co.pveJobs') == 0, "the job is done")
check(run('for _, c in ipairs(SENT) do if c.kind == "build" and c.p and c.p.kind == "removal" and c.player == 300 then return true end end return false') is True,
      "the removal is sent for the bankrupt company")
check(count_news(run, "pve_win") == 0, "no victory while ai:2 plays")
months(run, 3, "4")
check(count_news(run, "pve_win") == 1, "the last computer company out: the player wins")
check(run('return RMLIST') is not None, "ok")

if failures:
    print(f"FAIL: {len(failures)} check(s)")
    sys.exit(1)
print("PASS")
