-- Saves the project (with SINE's loaded-instrument state) and renders it with the project's
-- render settings. Run inside the REAPER instance where Ratio was loaded.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-RATIO-001]]
local marker = proj_dir .. [[/Provenance/render_done.txt]]

local tr = reaper.GetTrack(0, 0)
local _, fxname = reaper.TrackFX_GetFXName(tr, 0, "")
local _, preset = reaper.TrackFX_GetPreset(tr, 0, "")

reaper.Main_OnCommand(40026, 0) -- File: Save project
reaper.Main_OnCommand(41824, 0) -- File: Render project, using the most recent render settings

local f = io.open(marker, "w")
if f then
  f:write("fx=" .. tostring(fxname) .. "\n")
  f:write("preset=" .. tostring(preset) .. "\n")
  f:close()
end
