local renderDir=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Renders]]
local marker=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Provenance/stem_diag_done.txt]]
local tabla=nil
for i=0,reaper.CountTracks(0)-1 do
 local tr=reaper.GetTrack(0,i)
 local _,name=reaper.GetTrackName(tr)
 if name=="Tabla_Real_B" then tabla=tr end
 reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
 reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",0)
end
if not tabla then return end

local function setup(pattern)
 reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
 reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
 reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0.0,true)
 reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",89.0,true)
 reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
 reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
 reaper.GetSetProjectInfo_String(0,"RENDER_FILE",renderDir,true)
 reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN",pattern,true)
 reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
end

reaper.SetMediaTrackInfo_Value(tabla,"I_SOLO",1)
setup("DIAG-TABLA-ONLY")
reaper.Main_OnCommand(41824,0)
reaper.SetMediaTrackInfo_Value(tabla,"I_SOLO",0)

reaper.SetMediaTrackInfo_Value(tabla,"B_MUTE",1)
setup("DIAG-MELODY-ONLY")
reaper.Main_OnCommand(41824,0)
reaper.SetMediaTrackInfo_Value(tabla,"B_MUTE",0)

local f=io.open(marker,"w")
if f then f:write("done\n"); f:close() end
