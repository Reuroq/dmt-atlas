"""Independently close saved r3 arithmetic, identities and receipts; no replay."""
import os
import struct
import probe_centre_v34_staged_arithmetic_r3 as p
from check_centre_v34_staged_arithmetic_r3 import integer_add, frombit


def write(name, data):
    with (p.HERE/name).open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def main():
    p.gate();p.receipt('runtime')
    launch=p.read(p.PREFIX+'-runtime-once-launch.json')
    assert launch['preparation_sha256']==p.digest(p.PREFIX+'-preparation-integrity.json')
    manifest=p.PREFIX+'-runtime-integrity.json'
    assert not (p.HERE/manifest).exists()
    p.save(p.PREFIX+'-runtime-close-started.json',{'saved_only':True})
    result=p.read(p.PREFIX+'-result.json');p.verify(result['events'])
    names=list(result['events'])
    assert names==[p.PREFIX+'-event-'+str(i).zfill(3)+'.json' for i in range(387)]
    assert set(names)=={f.name for f in p.HERE.glob(p.PREFIX+'-event-*')}
    events=[];previous=None
    for name in names:
        e=p.read(name);assert e['previous_sha256']==previous
        previous=p.digest(name);events.append(e)
    assert [e['kind'] for e in events]==['inputs','browser-launch-intent','browser-launched','plan']+['step-intent','step-result','assessment']*126+['dispose-intent','dispose-result','dispose-assessment','page-closed','browser-closed']
    assert events[0]['payload']=={'seeds_sha256':p.digest(p.SEEDS),'texture_sha256':p.digest(p.TEXTURE),
        'synthetic_not_recovered_gpu_intermediates':True,'translated_queries':'omitted by protocol'}
    assert events[1]['payload']=={'args':p.ARGS} and events[2]['payload']['version']
    static=p.read(p.PREFIX+'-static.json');plan=static['plan']
    assert events[3]['payload']==plan and len(plan)==126
    raw=(p.HERE/p.TEXTURE).read_bytes()
    words=list(struct.unpack('<1024I',raw));texels=list(struct.unpack('<1024f',raw))
    assert words.count(0)==905 and words==p.source_bits()
    leaves=p.read(p.SEEDS)['leaves'];assessments=[];readbacks={};observations=[];kinds=[]
    vertex='varying vec2 sampleUV; void main(){sampleUV=uv;gl_Position=vec4(position.xy,0.,1.);}'
    for i,step in enumerate(plan):
        request,r,saved=[e['payload'] for e in events[4+i*3:7+i*3]]
        expected=dict(step)
        if step['op']=='shared':expected['dataBits']=words
        assert request==expected and r['step']==expected
        assert r['before']==r['after']=={'errors':[],'drained':True}
        assert r['contextLost'] is False and r['skipped'] is False and r['exception'] is None
        if step['op']=='renderer':kinds.append('renderer')
        if step['op']=='shared':kinds.extend(['target','texture','geometry'])
        if step['op']=='material':kinds.append('material')
        registry=[{'id':'resource-'+str(j),'kind':kind,'attempted':False,'succeeded':False,'error':None} for j,kind in enumerate(kinds)]
        assert r['resources']==registry
        v=r['value']
        if step['op']=='shared':
            assert p.exact_words(request['dataBits'],words) and p.exact_words(r['step']['dataBits'],words)
            assert p.exact_words(v['input']['bits'],words) and [p.bit(x) for x in v['input']['values']]==words
        if step['op']=='material':
            assert v['vertexShader']==vertex
            shader=('precision highp float; void main(){gl_FragColor=vec4(.125,-.5,2.,1.);}' if step['name']=='float-control'
                    else static['shader_sources'][step['leaf']][step['arm']])
            assert v['fragmentShader']==shader
        # Independently rebuild full binary32 expectations using exact rational addition.
        if step['op'].startswith('read-'):
            bits=v['bits'];assert len(bits)==len(v['values'])==512
            assert all(type(b) is int and 0<=b<=0xffffffff for b in bits)
            assert all(frombit(b)==x for b,x in zip(bits,v['values']))
            if step['name']=='float-control':
                assert bits==[p.bit(x) for x in [.125,-.5,2.,1.]*128]
            else:
                leaf=leaves[step['leaf']];xs=texels[leaf['row']*512:(leaf['row']+1)*512:4];want=[]
                for x in xs:
                    parent=integer_add(x,leaf['c1'])
                    child=integer_add(frombit(parent),leaf['c2'])
                    folded=integer_add(x,frombit(integer_add(leaf['c1'],leaf['c2'])))
                    want.extend([p.bit(x),parent,child,folded])
                all_bad=[j for j,(b,w) in enumerate(zip(bits,want)) if b!=w]
                unique_bad=[j for j in all_bad if j<leaf['count']*4]
                replay=[j for j in range(leaf['count']) if bits[j*4+2]!=integer_add(frombit(bits[j*4+1]),leaf['c2'])]
                obs={'step':step,'unique_components':leaf['count']*4,
                     'unique_mismatches_per_channel':[sum(j%4==c for j in unique_bad) for c in range(4)],
                     'full_mismatches_per_channel':[sum(j%4==c for j in all_bad) for c in range(4)],
                     'child_vs_parent_mismatches':len(replay),'full_exact':not all_bad}
                assert saved['all_texels']['expected_bits']==want
                assert saved['all_texels']['mismatched_components']==all_bad
                assert saved['unique']['mismatched_components']==unique_bad
                assert saved['unique']['child_vs_parent_failed_indices']==replay
                observations.append(obs)
        a=p.assess(r,leaves,texels,readbacks);assert a==saved;assessments.append(a)
    assert assessments==result['assessments']
    assert sum(a['classification']=='ok' for a in assessments)==122
    assert sum(a['classification']=='arithmetic-mismatch' for a in assessments)==4
    assert len(kinds)==9 and kinds==['renderer','target','texture','geometry']+['material']*5
    assert events[-5]['payload']=={}
    disposed=events[-4]['payload']
    assert disposed['step']=={'op':'dispose'}
    assert disposed['resources']==[dict(e,attempted=True,succeeded=True) for e in registry]
    assert p.cleanup_valid(disposed['value'],disposed['resources'])
    assert disposed['before']==disposed['after']=={'errors':[],'drained':True}
    assert disposed['exception'] is None and not disposed['skipped'] and not disposed['contextLost']
    assert p.assess(disposed,leaves,texels,{})==events[-3]['payload']=={'step':{'op':'dispose'},'classification':'ok'}
    assert events[-2]['payload']==events[-1]['payload']=={}
    assert result['complete'] and result['infrastructure_clean'] and result['failure'] is result['cleanup_failure'] is None
    warnings=result['browser_messages']
    assert len(warnings)==5 and all(m['kind']=='console' and m['type']=='warning' for m in warnings)
    assert sum('deprecated' in m['text'] for m in warnings)==1 and sum('GPU stall due to ReadPixels' in m['text'] for m in warnings)==4
    assert p.supported(assessments,True) and result['synthetic_uniform_candidate_supported']
    for leaf in (0,1):
        for method in ('read-three','read-raw'):
            arms={o['step']['arm']:o for o in observations if o['step']['leaf']==leaf and o['step']['op']==method}
            assert set(arms)=={'literal','uniform'}
            assert arms['literal']['unique_mismatches_per_channel']==[0,0,39 if leaf==0 else 49,0]
            assert arms['literal']['child_vs_parent_mismatches']==(39 if leaf==0 else 49)
            assert arms['uniform']['full_exact'] and arms['uniform']['child_vs_parent_mismatches']==0
    for key in ('numeric_passed','first_root_certified','capture_permitted'):assert result[key] is False
    assert result['new_images']==0
    next_work=('Verify centre-v34-staged-arithmetic-r3-runtime-integrity.json files/protected/display and runtime-close-once '
        'actual-exit0 receipt hashes. Synthetic both-leaf support now permits STATIC preparation of an isolated v35 '
        'candidate per centre-v34-followup-experiment-design.md section A: change only the two second-offset literals '
        'to runtime uniforms, with declarations/bindings covered everywhere, preserving v34 shape, materials and all '
        'strict numerical gates. Freeze new versioned fixtures/runners and close static checks before any field runtime. '
        'Do not presume the four original root failures fixed; review existing local-profile evidence and section B '
        'before designing any additive strict root isolation. No historical replay, tolerance relaxation, live promotion '
        'or roots/cost/capture/acceptance bypass.')
    summary=('Distinct staged arithmetic r3 runtime CLOSED actual exit0; 126 stages/387 chained events verified saved-only. '
        'All 1024 source/request/CPU uint32 words exact, including 905 positive-zero components. Both read APIs agree. '
        'Literal arms fail only child channel: 39 axial and 49 angular unique samples; both uniform arms exact over '
        'all 128 texels against independent rational binary32 oracle. Unchanged both-leaf synthetic support criterion PASS. '
        'All GL intervals clean; nine registered disposable identities attempted successfully once, renderer last; '
        'page/browser close recorded. One Three deprecation and four ReadPixels stall warnings; no page/console errors. '
        'Disposal calls returning successfully are not a GPU leak proof. Synthetic support is not compiler attribution '
        'or field/root/cost/visual acceptance. Frozen r2 and original exact-jet/716-of-720 failures unchanged. '
        'latest unchanged inspected REJECTED GAME v33r6; all19 unfinished.')
    review={'saved_evidence_verified':True,'summary':summary,'next_work':next_work,'observations':observations,
        'events':len(events),'stages':len(plan),'resource_disposal':disposed['value'],'browser_messages':warnings,
        'synthetic_uniform_candidate_supported':True,'numeric_passed':False,'first_root_certified':False,
        'capture_permitted':False,'new_images':0}
    p.save(p.PREFIX+'-runtime-review.json',review)
    write(p.PREFIX+'-runtime-review.md',('# Arithmetic r3 runtime closure\n\n'+summary+'\n\n'
        'Closure independently checks original texture words, exact source/CPU bits, original shader arms, every '
        'readback against the rational oracle, all saved assessments, operation/resource identities, exact event '
        'order and hash chain, disposal order and browser lifecycle. No runtime or image replay.\n\n'
        '## Next bounded phase\n\n'+next_work+'\n').encode())
    prep=p.read(p.PREFIX+'-preparation-integrity.json')
    notes=(p.HERE/'NOTES.md').read_bytes();assert notes.startswith(b'\xef\xbb\xbf')
    head,old_next=notes.decode('utf-8-sig').split('## Exact next bounded work\n')
    assert 'run_centre_v34_staged_arithmetic_r3_once.py runtime ONCE' in old_next
    head='# Active: REDIRECT4 — arithmetic r3 runtime CLOSED; synthetic uniform support PASS\n'+head.split('\n',1)[1]
    head+='## Distinct staged arithmetic r3 runtime CLOSED — synthetic support PASS\n- '+summary+'\n'
    head+='- Verified preparation1214 evidence/16protected/4display plus runtime receipt hashes. Prior display archived; NOTES once/BOM retained.\n\n'
    readme=(p.HERE/'README.md').read_text()
    anchors=[line for line in readme.splitlines() if line.startswith('Distinct [staged arithmetic r3 preparation]')]
    assert len(anchors)==1
    assert 'staged arithmetic r3 preparation CLOSED static PASS' in (p.HERE/'status.txt').read_text()
    replacement=('Distinct [staged arithmetic r3 runtime]('+p.PREFIX+'-runtime-review.md) is **CLOSED actual exit0; synthetic uniform support PASS**. '
        'Both uniform arms exact; literal child-only mismatches 39 axial/49 angular. All 126 stages and nine disposal identities verified. '
        'No field, root, visual or acceptance pass; original failures retained.')
    updates={'NOTES.md':b'\xef\xbb\xbf'+(head+'## Exact next bounded work\n'+next_work+'\n').encode(),
        'README.md':readme.replace(anchors[0],replacement,1).encode(),'status.txt':(summary+' '+next_work+'\n').encode()}
    archives={}
    for name in updates:
        archive=name+'-before-'+p.PREFIX+'-runtime';write(archive,(p.HERE/name).read_bytes());archives[archive]=p.digest(archive)
    for name,data in updates.items():
        with (p.HERE/name).open('wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    files=dict(prep['files']);files[p.PREFIX+'-preparation-integrity.json']=p.digest(p.PREFIX+'-preparation-integrity.json')
    files.update({f.name:p.digest(f.name) for f in p.HERE.glob(p.PREFIX+'-*') if f.is_file() and not f.name.startswith(p.PREFIX+'-runtime-close-once')})
    files.update(archives)
    for name in ('close_centre_v34_staged_arithmetic_r3_runtime.py','run_centre_v34_staged_arithmetic_r3_runtime_close_once.py'):files[name]=p.digest(name)
    p.verify(files);p.verify(prep['protected']);assert p.digest('latest.png')==prep['display']['latest.png']
    display={n:p.digest(n) for n in prep['display']}
    p.save(manifest,{'files':files,'protected':prep['protected'],'display':display,'prior_display':prep['display'],
        'archived_display':archives,'runtime_run':True,'actual_exit':0,'saved_evidence_verified':True,
        'synthetic_uniform_candidate_supported':True,'numeric_passed':False,'first_root_certified':False,
        'capture_permitted':False,'new_images':0})
    for key in ('files','protected','display'):p.verify(p.read(manifest)[key])
    print('R3 saved-only runtime closure PASS:',len(files),'evidence hashes; synthetic support only')


if __name__=='__main__':main()
