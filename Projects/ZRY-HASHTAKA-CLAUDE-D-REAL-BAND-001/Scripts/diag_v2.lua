local out=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Provenance/diag_v2.txt]]
local f=io.open(out,"w")
for i=0,reaper.CountTracks(0)-1 do
 local tr=reaper.GetTrack(0,i)
 local _,name=reaper.GetTrackName(tr)
 local ni=reaper.CountTrackMediaItems(tr)
 f:write(string.format("%d %s items=%d mute=%.0f solo=%.0f vol=%.6f pan=%.3f mainsend=%.0f\n",i,name,ni,reaper.GetMediaTrackInfo_Value(tr,"B_MUTE"),reaper.GetMediaTrackInfo_Value(tr,"I_SOLO"),reaper.GetMediaTrackInfo_Value(tr,"D_VOL"),reaper.GetMediaTrackInfo_Value(tr,"D_PAN"),reaper.GetMediaTrackInfo_Value(tr,"B_MAINSEND")))
 for j=0,ni-1 do
  local it=reaper.GetTrackMediaItem(tr,j)
  local tk=reaper.GetActiveTake(it)
  local src=reaper.GetMediaItemTake_Source(tk)
  local typ=reaper.GetMediaSourceType(src,"")
  local _,fn=reaper.GetMediaSourceFileName(src,"")
  local ok,n,c,s=reaper.MIDI_CountEvts(tk)
  f:write(string.format("  item%d type=%s file=%s notes=%s pos=%.3f len=%.3f mute=%.0f\n",j,tostring(typ),tostring(fn),tostring(n),reaper.GetMediaItemInfo_Value(it,"D_POSITION"),reaper.GetMediaItemInfo_Value(it,"D_LENGTH"),reaper.GetMediaItemInfo_Value(it,"B_MUTE")))
 end
end
f:close()
