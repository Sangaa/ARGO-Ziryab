-- Opens ZRY-FIRST-BREATH-003-FLUTE-ANSWER.rpp, applies track gains from Provenance/track_gains.txt
-- (name<TAB>linear gain; absent = unity), renders each track solo as a stem, then the full
-- mix, saves, writes Provenance/render_done.txt and quits REAPER.
-- Run: reaper.exe -nosplash -new "<this file>". Archive Renders/ before running.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-FIRST-BREATH-003-FLUTE-ANSWER]]
local rpp = proj_dir .. [[/ZRY-FIRST-BREATH-003-FLUTE-ANSWER.rpp]]
local marker = proj_dir .. [[/Provenance/render_done.txt]]
local log = {}
local function L(s) log[#log + 1] = s end

reaper.Main_openProject(rpp)
local n = reaper.CountTracks(0)
L("tracks=" .. n)

local gains = {}
local gf = io.open(proj_dir .. [[/Provenance/track_gains.txt]], "r")
if gf then
  for line in gf:lines() do
    local name, g = line:match("^(%S+)%s+([%d%.%-eE]+)")
    if name and g then gains[name] = tonumber(g) end
  end
  gf:close()
end

for i = 0, n - 1 do
  local tr = reaper.GetTrack(0, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
  local g = gains[name] or 1.0
  reaper.SetMediaTrackInfo_Value(tr, "D_VOL", g)
  reaper.TrackFX_Show(tr, 0, 2)
  L(string.format("gain\t%s\t%.6f", name, g))
end

local function render(pattern)
  reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", pattern, true)
  reaper.Main_OnCommand(41824, 0) -- Render project, using the most recent render settings
  L("rendered\t" .. pattern)
end

for i = 0, n - 1 do
  for j = 0, n - 1 do
    reaper.SetMediaTrackInfo_Value(reaper.GetTrack(0, j), "I_SOLO", (i == j) and 2 or 0)
  end
  local _, name = reaper.GetSetMediaTrackInfo_String(reaper.GetTrack(0, i), "P_NAME", "", false)
  render("ZRY-FIRST-BREATH-003-FLUTE-ANSWER-stem-" .. name)
end
for j = 0, n - 1 do reaper.SetMediaTrackInfo_Value(reaper.GetTrack(0, j), "I_SOLO", 0) end
render("ZRY-FIRST-BREATH-003-FLUTE-ANSWER-mix")

reaper.Main_OnCommand(40026, 0) -- File: Save project (after everything, so quit sees a clean project)
local f = io.open(marker, "w")
if f then f:write(table.concat(log, "\n") .. "\n"); f:close() end
reaper.Main_OnCommand(40004, 0) -- File: Quit REAPER
