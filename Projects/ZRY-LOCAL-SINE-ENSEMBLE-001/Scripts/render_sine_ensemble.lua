-- Saves the project, then renders each track solo to Renders/ZRY-SINE-<track name>.wav.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001]]
local marker = proj_dir .. [[/Provenance/render_done.txt]]

for i = 0, reaper.CountTracks(0) - 1 do
  reaper.TrackFX_Show(reaper.GetTrack(0, i), 0, 2)
end
reaper.Main_OnCommand(40026, 0) -- File: Save project

local n = reaper.CountTracks(0)
local log = {}
for i = 0, n - 1 do
  for j = 0, n - 1 do
    reaper.SetMediaTrackInfo_Value(reaper.GetTrack(0, j), "I_SOLO", (i == j) and 2 or 0)
  end
  local _, name = reaper.GetSetMediaTrackInfo_String(reaper.GetTrack(0, i), "P_NAME", "", false)
  reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "ZRY-SINE-" .. name, true)
  reaper.Main_OnCommand(41824, 0) -- Render with the project's render settings
  log[#log + 1] = name
end
for j = 0, n - 1 do reaper.SetMediaTrackInfo_Value(reaper.GetTrack(0, j), "I_SOLO", 0) end
reaper.Main_OnCommand(40026, 0)

local f = io.open(marker, "w")
if f then f:write(table.concat(log, "\n") .. "\n"); f:close() end
