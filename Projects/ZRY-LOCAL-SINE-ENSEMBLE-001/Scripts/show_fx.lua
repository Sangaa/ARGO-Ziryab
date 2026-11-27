-- Opens SINE Player's window for the track number in Provenance/show_fx_track.txt (1-based),
-- closing every other FX window first. Used while loading instruments by hand.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001]]
local f = io.open(proj_dir .. [[/Provenance/show_fx_track.txt]], "r")
local n = f and tonumber(f:read("*l")) or 1
if f then f:close() end
for i = 0, reaper.CountTracks(0) - 1 do
  reaper.TrackFX_Show(reaper.GetTrack(0, i), 0, 2)
end
local tr = reaper.GetTrack(0, n - 1)
if tr then reaper.TrackFX_Show(tr, 0, 3) end
