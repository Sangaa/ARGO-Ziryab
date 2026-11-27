-- The first ensemble render clipped Strand_Nylon (164 samples at full scale).
-- Lower that track by 6.02 dB, then run the normal render script.
for i = 0, reaper.CountTracks(0) - 1 do
  local tr = reaper.GetTrack(0, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
  if name == "Strand_Nylon" then reaper.SetMediaTrackInfo_Value(tr, "D_VOL", 0.5) end
end
dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001/Scripts/render_sine_ensemble.lua]])
