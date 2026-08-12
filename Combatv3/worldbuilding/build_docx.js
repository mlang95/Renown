const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
        PageBreak, ImageRun, PageOrientation } = require('docx');

const B = JSON.parse(fs.readFileSync('book.json', 'utf8'));
const INK='1C1C20', MUTE='6B6B73', RULE='C9C6BF', BAND='EFECE5';
const DOM={Prowess:'9E2B25',Cunning:'1C1C20',Industry:'2E5A8C',Piety:'B8901F'};

const W = 9746, CW = [2100, 7646];
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top:none,bottom:none,left:none,right:none,
                    insideHorizontal:none, insideVertical:none };

const p = (text, o={}) => new Paragraph({
  spacing:{after:o.after??140, line:o.line??300}, alignment:o.align,
  heading:o.heading, pageBreakBefore:o.pb,
  border:o.rule?{bottom:{style:BorderStyle.SINGLE,size:6,color:o.ruleColor||RULE,space:6}}:undefined,
  children:[new TextRun({ text, bold:o.bold, italics:o.italic, size:o.size??21,
                          color:o.color??INK, font:'Georgia' })]});

const h1 = (t,o={}) => p(t,{heading:HeadingLevel.HEADING_1,size:48,bold:true,pb:o.pb!==false,
                            rule:true,color:o.color||INK,after:240});
const paras = (v,o={}) => (Array.isArray(v)?v:(v?[v]:[])).forEach(t=>sect.push(p(t,o)));

const sect = [];

// ---- title
sect.push(new Paragraph({spacing:{before:3200,after:200},alignment:AlignmentType.CENTER,
  children:[new TextRun({text:'RENOWN',bold:true,size:92,font:'Georgia',color:INK})]}));
sect.push(p('the world, its ages, and its fifteen peoples',
  {align:AlignmentType.CENTER,color:MUTE,size:22,after:0}));

// ==================================================== 1. HOOK
sect.push(h1('The Hook'));
paras(B.hook,{size:23,line:340});

// ==================================================== 2. PREMISE
sect.push(h1('The Premise'));
paras(B.premise,{size:23,line:340});

// ==================================================== 3. OVERVIEW  (fifteen peoples at a glance)
// B.overview = [{title, entries:[{name, domains, text}]}]
sect.push(h1('The Overview'));
(B.overview||[]).forEach(th=>{
  sect.push(p(th.title,{heading:HeadingLevel.HEADING_2,size:30,bold:true,after:120}));
  (th.entries||[]).forEach(e=>{
    sect.push(p(e.name,{bold:true,size:21,after:20}));
    if (e.domains && e.domains.length)
      sect.push(p(e.domains.join(' / '),{color:MUTE,size:16,after:60}));
    sect.push(p(e.text,{after:160}));
  });
});

// ==================================================== 4. MAP  (map + all geography)
sect.push(h1('The Map'));
if (fs.existsSync('/mnt/user-data/uploads/map7.png')) {
  sect.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:200},
    children:[new ImageRun({type:'png',data:fs.readFileSync('/mnt/user-data/uploads/map7.png'),
      transformation:{width:600,height:338}})]}));
}
if (B.sea) sect.push(p(B.sea,{}));
(B.land||[]).forEach(g=>{
  sect.push(p(`${g.corner} — ${g.where}`,{heading:HeadingLevel.HEADING_2,size:30,bold:true,
    color:DOM[g.corner]||INK,after:120}));
  g.places.forEach(pl=>{ sect.push(p(pl.name,{bold:true,size:21,after:40}));
                         sect.push(p(pl.text,{after:160})); });
});
if ((B.stretches||[]).length || (B.isles||[]).length){
  sect.push(p('The Sea, and the Isles',{heading:HeadingLevel.HEADING_2,size:30,bold:true,after:120}));
  (B.stretches||[]).concat(B.isles||[]).forEach(pl=>{
    sect.push(p(pl.name,{bold:true,size:21,after:40}));
    sect.push(p(pl.text,{after:160})); });
}

// ==================================================== 5. TIMELINE
sect.push(h1('The Reckoning'));
B.ages.forEach(a=>{
  sect.push(new Table({ columnWidths:[W], width:{size:W,type:WidthType.DXA},
    borders:{...noBorders, left:{style:BorderStyle.SINGLE,size:18,color:DOM[a.domain]||MUTE}},
    rows:[new TableRow({children:[new TableCell({ width:{size:W,type:WidthType.DXA},
      shading:{type:ShadingType.CLEAR,fill:BAND},margins:{top:90,bottom:90,left:140,right:140},
      children:[p(a.name,{bold:true,size:26,after:0}),
                p(a.span,{color:MUTE,size:18,after:0})]})]})]}));
  sect.push(p('',{after:80}));
  if (a.events.length) sect.push(new Table({ columnWidths:CW, width:{size:W,type:WidthType.DXA},
    borders:noBorders,
    rows:a.events.map(e=>new TableRow({children:[
      new TableCell({width:{size:CW[0],type:WidthType.DXA},margins:{top:60,bottom:60,right:120},
        children:[p(e.year,{bold:true,size:18,after:0})]}),
      new TableCell({width:{size:CW[1],type:WidthType.DXA},margins:{top:60,bottom:60,left:160},
        borders:{...noBorders,left:{style:BorderStyle.SINGLE,size:4,color:RULE}},
        children:[p(e.text,{size:18,line:250,after:0})]})]}))}));
  sect.push(p('',{after:200}));
});

// ==================================================== 6. THE FIFTEEN CULTURES (deep)
B.threads.forEach(th=>{
  sect.push(p(th.title,{heading:HeadingLevel.HEADING_1,size:48,bold:true,pb:true,rule:true,after:240}));
  th.prose.forEach(t=>sect.push(p(t,{size:23,line:340})));
  th.cultures.forEach(c=>{
    const col = c.domains.length===1 ? (DOM[c.domains[0]]||INK) : INK;
    sect.push(p(c.name,{heading:HeadingLevel.HEADING_1,size:48,bold:true,color:col,pb:true,after:40}));
    sect.push(p(`${c.type} · ${c.domains.join(' / ')} · ${c.region}`,
      {color:MUTE,size:18,rule:true,ruleColor:col,after:240}));
    if (c.rows.length) sect.push(new Table({ columnWidths:CW, width:{size:W,type:WidthType.DXA},
      borders:{...noBorders, insideHorizontal:{style:BorderStyle.SINGLE,size:2,color:RULE}},
      rows:c.rows.map(r=>new TableRow({children:[
        new TableCell({width:{size:CW[0],type:WidthType.DXA},margins:{top:70,bottom:70,right:120},
          children:[p(r[0],{bold:true,size:17,after:0})]}),
        new TableCell({width:{size:CW[1],type:WidthType.DXA},margins:{top:70,bottom:70},
          children:[p(r[1],{size:17,line:240,after:0})]})]}))}));
    sect.push(p('',{after:200}));
    if (c.overview) sect.push(p(c.overview,{size:23,line:340}));
    c.sections.concat(c.rivals.length?[{head:'Rivals',text:''}]:[]).forEach(s=>{
      if (s.text===''){ sect.push(p(s.head,{heading:HeadingLevel.HEADING_2,size:26,bold:true,after:100}));
        c.rivals.forEach(r=>sect.push(p(`${r.head} — ${r.text}`,{})));
      } else { sect.push(p(s.head,{heading:HeadingLevel.HEADING_2,size:26,bold:true,after:100}));
        sect.push(p(s.text,{})); }});
    if (c.holdings.length){ sect.push(p('Holdings',{heading:HeadingLevel.HEADING_2,size:26,bold:true,after:100}));
      sect.push(p(c.holdings.join(', '),{})); }
    c.events.forEach(e=>{ sect.push(p(e.head,{heading:HeadingLevel.HEADING_2,size:26,bold:true,after:100}));
      sect.push(p(e.text,{})); });
  });
});

// ==================================================== 7. AGE OF DARKNESS (deep lore)
// B.darkness = {name, dating, blocks:[{head, text}]}
if (B.darkness && (B.darkness.blocks||[]).length){
  sect.push(h1(B.darkness.name || 'The Age of Darkness'));
  if (B.darkness.dating) sect.push(p(B.darkness.dating,{color:MUTE,size:18,after:200}));
  B.darkness.blocks.forEach(s=>{
    if (s.head) sect.push(p(s.head,{heading:HeadingLevel.HEADING_2,size:26,bold:true,after:100}));
    if (s.text) sect.push(p(s.text,{size:23,line:340}));
  });
}

const doc = new Document({ sections:[{ properties:{ page:{ margin:{top:1080,right:1080,bottom:1080,left:1080} } },
                                       children:sect }] });
Packer.toBuffer(doc).then(b=>{ fs.writeFileSync('renown_world.docx', b);
  console.log('renown_world.docx —', (b.length/1024).toFixed(0)+'KB'); });
