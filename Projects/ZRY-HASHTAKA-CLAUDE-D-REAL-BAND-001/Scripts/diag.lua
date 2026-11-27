local out = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Provenance/diag_tracks.txt]]
local f=io.open(out,"w")
if not f then return end
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  local ni=reaper.CountTrackMediaItems(tr)
  local fxn=reaper.TrackFX_GetCount(tr)
  f:write(string.format("TRACK %d %s items=%d fx=%d vol=%.6f pan=%.3f\n",i,name,ni,fxn,reaper.GetMediaTrackInfo_Value(tr,"D_VOL"),reaper.GetMediaTrackInfo_Value(tr,"D_PAN")))
  for j=0,ni-1 do
    local it=reaper.GetTrackMediaItem(tr,j)
    local tk=reaper.GetActiveTake(it)
    if tk then
      local src=reaper.GetMediaItemTake_Source(tk)
      local typ=reaper.GetMediaSourceType(src,"")
      local ok,notes,cc,syx=reaper.MIDI_CountEvts(tk)
      f:write(string.format("  ITEM %d type=%s midi_ok=%s notes=%s cc=%s syx=%s pos=%.3f len=%.3f\n",j,tostring(typ),tostring(ok),tostring(notes),tostring(cc),tostring(syx),reaper.GetMediaItemInfo_Value(it,"D_POSITION"),reaper.GetMediaItemInfo_Value(it,"D_LENGTH")))
    end
  end
  for fx=0,fxn-1 do
    local _,fxname=reaper.TrackFX_GetFXName(tr,fx,"")
    local enabled=reaper.TrackFX_GetEnabled(tr,fx)
    local offline=reaper.TrackFX_GetOffline(tr,fx)
    local pok,preset=reaper.TrackFX_GetPreset(tr,fx,"")
    f:write(string.format("  FX %d name=%s enabled=%s offline=%s preset_ok=%s preset=%s\n",fx,tostring(fxname),tostring(enabled),tostring(offline),tostring(pok),tostring(preset)))
  end
end
f:close()
