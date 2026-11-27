local events = dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Scripts/score_events.lua]])
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001/Auditions]]
local rpp=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001/Auditions/OUD_AUDITION.rpp]]
while reaper.CountTracks(0)>0 do reaper.DeleteTrack(reaper.GetTrack(0,0)) end
reaper.InsertTrackAtIndex(0,true)
local tr=reaper.GetTrack(0,0)
reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","Turkish_Oud",true)

local fx=reaper.TrackFX_AddByName(tr,"VST3i: DSK World String (DSK Music)",false,-1)
if fx<0 then
  fx=reaper.TrackFX_AddByName(tr,"DSK World String",false,-1)
end
if fx<0 then reaper.ShowConsoleMsg("FAIL FX\n"); return end
reaper.TrackFX_SetPresetByIndex(tr,fx,12)

local startT=7.55
local endT=15.45
local dur=(endT-startT)+1.0
local item=reaper.CreateNewMIDIItemInProj(tr,0,dur,false)
local take=reaper.GetActiveTake(item)
local count=0
for _,e in ipairs(events["Strand_Nylon"]) do
  if e[1]>=startT and e[1]<endT then
    local a=e[1]-startT+0.25
    local b=e[2]-startT+0.25
    local pp0=reaper.MIDI_GetPPQPosFromProjTime(take,a)
    local pp1=reaper.MIDI_GetPPQPosFromProjTime(take,b)
    reaper.MIDI_InsertNote(take,false,false,pp0,pp1,0,e[3],math.min(110,e[4]+12),true)
    count=count+1
  end
end
reaper.MIDI_Sort(take)
reaper.SetMediaTrackInfo_Value(tr,"D_VOL",0.85)

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",dur,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","01_OUD_TURKISH_HASHTAKA_PHRASE",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
reaper.Main_SaveProjectEx(0,rpp,8)
reaper.Main_OnCommand(41824,0)

local f=io.open(outdir.."/OUD_AUDITION_META.txt","w")
if f then
  local ok,pn=reaper.TrackFX_GetPreset(tr,fx,"")
  f:write("fx="..tostring(fx).."\n")
  f:write("preset="..tostring(pn).."\n")
  f:write("preset_index=12\n")
  f:write("notes="..tostring(count).."\n")
  f:write("phrase_source=HASHTAKA Strand_Nylon notes "..startT.." to "..endT.." sec\n")
  f:close()
end
