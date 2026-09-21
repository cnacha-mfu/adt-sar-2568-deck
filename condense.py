import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def replace_section(fname, marker, new_html):
    s = open(fname, encoding="utf-8").read()
    i = s.index(f"<!-- {marker} ")
    j = s.find("\n<!-- ", i + 5)
    if j == -1: j = len(s)
    s = s[:i] + new_html.rstrip("\n") + "\n" + s[j:]
    open(fname, "w", encoding="utf-8").write(s)
    print("replaced", marker)

S03 = '''<!-- 03 ทิศทางองค์กร -->
<section class="s" data-cap="วิสัยทัศน์ · TEAM · SO 8 ข้อ">
  <div class="head"><div class="eyebrow">P.1ก(2) · หมวด 2.1ข · ทิศทางองค์กร</div><h1 class="t">วิสัยทัศน์เดียว ค่านิยม T.E.A.M. และ SO 8 ข้อ ที่ทุกหมวดบูรณาการกลับมาหา</h1><div class="sub">ควบรวม SO จาก 14 เหลือ 8 ข้อ · ตัวชี้วัด 33 ตัวผูกแผนพัฒนา มฟล. ติดตามผ่านระบบ BI</div></div>
  <div class="body row" style="gap:14px">
    <div class="col" style="flex:0 0 430px;gap:10px">
      <div class="card n" style="padding:14px 16px">
        <div class="lbl">วิสัยทัศน์</div>
        <div style="font-size:16px;font-weight:500;line-height:1.4;margin-top:4px">ผู้นำด้านการศึกษา วิจัย และนวัตกรรมดิจิทัล เพื่อขับเคลื่อน <span style="color:var(--gold-l)">Digital Valley</span> แห่งภาคเหนือ</div>
      </div>
      <div class="card" style="padding:12px 14px;flex:1">
        <div class="lbl">ค่านิยม MFU First + T.E.A.M.</div>
        <div class="row" style="gap:8px;margin-top:8px">
          <div class="grow" style="text-align:center"><div class="big" style="font-size:26px;color:var(--gold-d)">T</div><div class="note" style="font-size:11px">Trust</div></div>
          <div class="grow" style="text-align:center"><div class="big" style="font-size:26px;color:var(--gold-d)">E</div><div class="note" style="font-size:11px">Excellence</div></div>
          <div class="grow" style="text-align:center"><div class="big" style="font-size:26px;color:var(--gold-d)">A</div><div class="note" style="font-size:11px">Agility</div></div>
          <div class="grow" style="text-align:center"><div class="big" style="font-size:26px;color:var(--gold-d)">M</div><div class="note" style="font-size:11px">Mutual Respect</div></div>
        </div>
        <div class="note" style="margin-top:8px;border-top:1px solid var(--rule2);padding-top:6px"><span class="tag">Learning</span> ปี 2568 ปรับ T จาก Teamwork เป็น Trust จากเสียงบุคลากร · การรับรู้ค่านิยม <b>4.15</b> · วิสัยทัศน์ <b>4.23</b> (เป้า 4)</div>
      </div>
    </div>
    <div class="grow col" style="gap:8px">
      <div class="lbl">วัตถุประสงค์เชิงกลยุทธ์ (SO) 8 ข้อ · ตาราง 2-2</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;flex:1">
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO1</div><div class="txt" style="font-size:12.5px"><b>ผู้นำวิจัยเชิงลึก</b> AI · IoT · Digital Health · ARIC</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO2</div><div class="txt" style="font-size:12.5px"><b>วิจัยตอบโจทย์พื้นที่</b> ทุนภายนอก 12.14 ลบ. (เป้า 6.5)</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO3</div><div class="txt" style="font-size:12.5px"><b>บัณฑิตคุณภาพสูง</b> ปรับปรุง 3 หลักสูตรครบวงรอบ</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO4</div><div class="txt" style="font-size:12.5px"><b>เรียนรู้ตลอดชีวิต + สากล</b> Non-degree · EMI · Outbound 4.23%</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO5</div><div class="txt" style="font-size:12.5px"><b>สมรรถนะบุคลากร</b> ป.เอก 78.9% · ตำแหน่งวิชาการ 57.9%</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO6</div><div class="txt" style="font-size:12.5px"><b>ถ่ายทอดความรู้สู่สังคม</b> ผู้รับบริการ &gt;310 คน</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO7</div><div class="txt" style="font-size:12.5px"><b>เครือข่ายนานาชาติ</b> MoU 6 ฉบับ 5 ประเทศ</div></div>
        <div class="card" style="padding:9px 12px"><div class="mono gold" style="font-size:11px">SO8</div><div class="txt" style="font-size:12.5px"><b>บริหารมีประสิทธิภาพ</b> เบิกจ่าย 52.54% vs มฟล. 34.10%</div></div>
      </div>
    </div>
  </div>
</section>
'''

S06 = '''<!-- 06 หมวด 2 -->
<section class="s" data-cap="หมวด 2 กลยุทธ์">
  <div class="head"><div class="eyebrow">หมวด 2 · กลยุทธ์ · SO → แผนปฏิบัติการ → งบประมาณ → ตัวชี้วัด</div><h1 class="t">กลยุทธ์ถูกแปลงเป็นแผนปฏิบัติการ 28 รายการ จัดสรรงบด้วยเกณฑ์ที่ประกาศไว้ล่วงหน้า และติดตามผลจริงรายโครงการ</h1><div class="sub">ตาราง 2-1 กระบวนการวางแผน 6 ขั้น · ประกาศสำนักวิชา เรื่อง Strategic Priority Scoring (ลงนามคณบดี)</div></div>
  <div class="body row" style="gap:14px">
    <div class="grow col" style="gap:10px">
      <div class="step">
        <div class="st"><div class="num">01 · ต.ค.</div><div class="nm">วิเคราะห์ PEST/SWOT</div><div class="who">กก.แผนกลยุทธ์</div></div>
        <div class="st"><div class="num">02</div><div class="nm">ทบทวน SO 8 ข้อ + เป้า</div><div class="who">คณบดี · ประธานหลักสูตร</div></div>
        <div class="st"><div class="num">03</div><div class="nm">เสนอโครงการ · ให้คะแนน</div><div class="who">หัวหน้าคณะทำงาน 6 ชุด</div></div>
        <div class="st"><div class="num">04</div><div class="nm">จัดสรรงบตามคะแนน</div><div class="who">บอร์ดอนุมัติ · ส่วนแผน</div></div>
        <div class="st"><div class="num">05 · ไตรมาส</div><div class="nm">ติดตาม Q1–Q4 + Final Report</div><div class="who">เลขานุการ · ระบบ มฟล.</div></div>
        <div class="st"><div class="num">06 · ปลายปี</div><div class="nm">ปรับแผน (Trigger-based)</div><div class="who">บอร์ด · 3 กรณีปี 2568</div></div>
      </div>
      <div class="row" style="gap:10px;flex:1">
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">Priority Scoring · น้ำหนัก 4 มิติ</div>
          <div class="col" style="gap:6px;margin-top:8px">
            <div><div class="row" style="justify-content:space-between"><span class="txt" style="font-size:12.5px">Strategic Fit</span><span class="mono" style="font-size:12px">40</span></div><div class="bar"><i style="width:40%"></i></div></div>
            <div><div class="row" style="justify-content:space-between"><span class="txt" style="font-size:12.5px">Impact / Value</span><span class="mono" style="font-size:12px">30</span></div><div class="bar"><i style="width:30%"></i></div></div>
            <div><div class="row" style="justify-content:space-between"><span class="txt" style="font-size:12.5px">Feasibility</span><span class="mono" style="font-size:12px">15</span></div><div class="bar"><i class="g" style="width:15%"></i></div></div>
            <div><div class="row" style="justify-content:space-between"><span class="txt" style="font-size:12.5px">Efficiency</span><span class="mono" style="font-size:12px">15</span></div><div class="bar"><i class="g" style="width:15%"></i></div></div>
          </div>
          <div class="note" style="margin-top:8px">&ge;4.0 สูง · 3.0–3.99 กลาง · &lt;3.0 ทบทวน</div>
        </div>
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">งบปีงบ 2569 · 1,440,000 บาท · ผูก SO</div>
          <table class="t" style="font-size:12px;margin-top:4px">
            <tr><th>ด้าน</th><th class="n">บาท</th><th class="n">%</th></tr>
            <tr><td>แผนระดับสำนักวิชา</td><td class="n">404,000</td><td class="n">28.1</td></tr>
            <tr class="hl"><td>วิจัย (สูงสุด · SO1/2)</td><td class="n">252,000</td><td class="n">17.5</td></tr>
            <tr><td>บริการวิชาการ (SO6)</td><td class="n">175,000</td><td class="n">12.2</td></tr>
            <tr><td>กิจกรรม นศ. + วิเทศ</td><td class="n">249,000</td><td class="n">17.3</td></tr>
            <tr><td>PR + หลักสูตร 6</td><td class="n">360,000</td><td class="n">25.0</td></tr>
          </table>
        </div>
      </div>
    </div>
    <div class="col" style="flex:0 0 310px;gap:8px">
      <div class="card n" style="padding:12px 14px;flex:1">
        <div class="lbl">แผนปฏิบัติการ 2568 · ผลจริง</div>
        <div class="big" style="margin-top:4px">28<small style="color:#B9C6D8">รายการ · 2.36 ลบ.</small></div>
        <div class="row" style="gap:8px;margin-top:12px">
          <div class="grow"><div class="lbl">บรรลุเป้า</div><div class="big" style="font-size:24px">8/8</div></div>
          <div class="grow"><div class="lbl">พึงพอใจ</div><div class="big" style="font-size:24px">89.7<small style="color:#B9C6D8">%</small></div></div>
          <div class="grow"><div class="lbl">เบิกจ่าย</div><div class="big" style="font-size:24px">92.5<small style="color:#B9C6D8">%</small></div></div>
        </div>
        <div class="note" style="margin-top:8px">Final Report 8 โครงการที่ตรวจรับแล้ว · KPI 100% ใน 7 โครงการ · ผู้เข้าร่วม 362 คน</div>
      </div>
      <div class="card y" style="padding:10px 12px"><div class="lbl">Intelligent Risk · การคาดการณ์</div><div class="txt" style="font-size:12.5px;margin-top:3px"><b>ARIC</b> 2570–2574 ผ่านผู้ทรงคุณวุฒิ 4 ท่าน (สไลด์ 14) · ค่าเป้า 2568/2569 + คาดการณ์ 2570 ครบ 6 ตัวชี้วัดหลัก (ตาราง 2-4)</div></div>
    </div>
  </div>
</section>
'''

S07 = '''<!-- 07 หมวด 3 -->
<section class="s" data-cap="หมวด 3 ลูกค้า">
  <div class="head"><div class="eyebrow">หมวด 3 · ลูกค้า · เสียงของลูกค้า (VOC) → ความผูกพัน</div><h1 class="t">รับฟังลูกค้า 7 กลุ่มผ่านช่องทางที่มี SLA และรายงานตรงไปตรงมา: 3 ตัวเหนือเป้า 6 ตัวต่ำกว่าเป้า</h1><div class="sub">ตาราง 3.1 VOC 5 ขั้น · ตาราง 3.2–3.3 ช่องทาง/มาตรฐาน · ผลลัพธ์ตาราง 7.2-1 (เต็ม 5 เป้า 4)</div></div>
  <div class="body row" style="gap:14px">
    <div class="grow col" style="gap:10px">
      <div class="step">
        <div class="st"><div class="num">01</div><div class="nm">จำแนกลูกค้า 3 มิติ</div><div class="who">บอร์ด · ปีละครั้ง</div></div>
        <div class="st"><div class="num">02</div><div class="nm">รับฟังตามช่องทาง/SLA</div><div class="who">คณะทำงาน · ต่อเนื่อง</div></div>
        <div class="st"><div class="num">03</div><div class="nm">วิเคราะห์สำรวจ+ร้องเรียน</div><div class="who">เลขานุการ · ภาคละครั้ง</div></div>
        <div class="st"><div class="num">04</div><div class="nm">ตอบสนองตาม SLA</div><div class="who">คณบดี · 3–5 วัน</div></div>
        <div class="st"><div class="num">05</div><div class="nm">ทบทวนช่องทาง/เกณฑ์</div><div class="who">บอร์ด · ปลายปี</div></div>
      </div>
      <div class="row" style="gap:10px;flex:1">
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">ความพึงพอใจ 2568 · ตาราง 7.2-1</div>
          <table class="t" style="font-size:12px;margin-top:4px">
            <tr><th>ตัวชี้วัด</th><th class="n">2567</th><th class="n">2568</th><th>สถานะ</th></tr>
            <tr><td>ผู้ใช้บัณฑิต</td><td class="n">4.37</td><td class="n">4.37</td><td><span class="tag g">เหนือเป้า</span></td></tr>
            <tr><td>ผู้รับบริการวิชาการ · จัดการข้อร้องเรียน</td><td class="n">—</td><td class="n">4.52 · 4.25</td><td><span class="tag g">เหนือเป้า</span></td></tr>
            <tr><td>ห้องปฏิบัติการ</td><td class="n">3.47</td><td class="n">3.85</td><td><span class="tag b">ฟื้นตัว</span></td></tr>
            <tr><td>อาจารย์ที่ปรึกษา (ปรึกษา / ข้อมูล)</td><td class="n">3.92</td><td class="n">3.72 / 3.56</td><td><span class="tag r">ต่ำกว่าเป้า</span></td></tr>
            <tr><td>หลักสูตร · งานบริการสำนักวิชา</td><td class="n">—</td><td class="n">3.61 · 3.72</td><td><span class="tag r">ต่ำกว่าเป้า</span></td></tr>
            <tr><td>การสื่อสาร · วิธีรับฟังเสียงลูกค้า</td><td class="n">3.64</td><td class="n">3.56 · 3.43</td><td><span class="tag r">ต่ำกว่าเป้า</span></td></tr>
          </table>
        </div>
        <div class="col" style="flex:0 0 250px;gap:8px">
          <div class="card k" style="padding:9px 12px;flex:1"><div class="lbl">Learning จากตัวที่ต่ำกว่าเป้า</div><div class="txt" style="font-size:12px;margin-top:3px">ปรับ critical step ขั้น 02–04: เว็บใหม่ ≤3 คลิก · โครงการสื่อ PR เลขที่ 20 · ที่ปรึกษา ≥1 ครั้ง/ภาค · แบบสำรวจลูกค้าฉบับใหม่</div></div>
          <div class="card k" style="padding:9px 12px;flex:1"><div class="lbl">ความเป็นธรรม</div><div class="txt" style="font-size:12px;margin-top:3px">นศ.กลุ่มเปราะบาง <b>5 คน</b> ดูแลครบ · ข้อร้องเรียน <b>1 เรื่อง</b> แก้ไขในกำหนด ไม่เกิดซ้ำ</div></div>
        </div>
      </div>
    </div>
    <div class="col" style="flex:0 0 280px;gap:8px">
      <div class="ph" style="flex:1 1 0;min-height:0"><img src="img/alumni-meetup.jpg" alt="IT &amp; ADT Alumni Meetup 2026"><div class="cap">Alumni Meetup 2026 — ศิษย์เก่า 120+ คน</div></div>
      <div class="row" style="gap:8px">
        <div class="card n kpi grow" style="padding:9px 11px"><div class="lbl">เข้าถึงเพจ FB</div><div class="big" style="font-size:22px">664,124</div><div class="d">ส.ค. 68–ก.ค. 69</div></div>
        <div class="card n kpi grow" style="padding:9px 11px"><div class="lbl">คงอยู่ ตรี / บว.</div><div class="big" style="font-size:22px">85 / 100<small style="color:#B9C6D8">%</small></div><div class="d">เป้า 75</div></div>
      </div>
    </div>
  </div>
</section>
'''

S08 = '''<!-- 08 หมวด 4 -->
<section class="s" data-cap="หมวด 4 การวัด วิเคราะห์ KM">
  <div class="head"><div class="eyebrow">หมวด 4 · การวัด วิเคราะห์ และการจัดการความรู้ · จาก Band 1 ปี 2567</div><h1 class="t">ตัวชี้วัด 33 ตัวถูกเลือกด้วยเกณฑ์ ติดตามผ่านแดชบอร์ด และเทียบกับแหล่งภายนอก 3 ระดับที่ระบุชื่อได้</h1><div class="sub">ตาราง 4.1-1 บริหารตัวชี้วัด 6 ขั้น (5W1H) · ตาราง 4.1-2 คู่เทียบ · ตาราง 4.2-3 KM 5 ขั้น</div></div>
  <div class="body row" style="gap:14px">
    <div class="grow col" style="gap:10px">
      <div class="step">
        <div class="st"><div class="num">01</div><div class="nm">เลือก KPI เกณฑ์ 4 ข้อ</div><div class="who">เชื่อม SO · SMART · มีคู่เทียบ</div></div>
        <div class="st"><div class="num">02</div><div class="nm">Data Owner + นิยาม</div><div class="who">เลขานุการ · ศูนย์ ICT</div></div>
        <div class="st"><div class="num">03</div><div class="nm">ทวนสอบ 5 มิติ</div><div class="who">Data Owner · ไตรมาส</div></div>
        <div class="st"><div class="num">04</div><div class="nm">แดชบอร์ด BI + Check-in</div><div class="who">Leading รายวัน · Lagging ไตรมาส</div></div>
        <div class="st"><div class="num">05</div><div class="nm">ทบทวน 4 เวที (Why-Why)</div><div class="who">Operational → Strategic</div></div>
        <div class="st"><div class="num">06</div><div class="nm">จัดลำดับปรับปรุง</div><div class="who">ผลกระทบ × เร่งด่วน × เป็นไปได้</div></div>
      </div>
      <div class="row" style="gap:10px;flex:1">
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">คู่เทียบ 3 ระดับ (ตาราง 4.1-2)</div>
          <table class="t" style="font-size:12px;margin-top:4px">
            <tr><th>ระดับ</th><th>แหล่ง</th><th>ใช้เทียบ</th></tr>
            <tr><td>ภายใน มฟล.</td><td>ระบบ BI — 15 สำนักวิชา</td><td>Exit Exam · มีงานทำ · Scopus · เบิกจ่าย</td></tr>
            <tr class="hl"><td>เครือข่าย</td><td><b>AUN Benchmark คณะไอที 12 สถาบัน</b></td><td>EdPEx ระดับสำนักวิชา (ปีแรก)</td></tr>
            <tr><td>สากล</td><td>Scopus · <b>OpenAlex</b> · THE</td><td>ตีพิมพ์ CS เทียบ 7 สถาบัน</td></tr>
          </table>
          <div class="row" style="gap:8px;margin-top:10px">
            <div class="grow"><span class="tag b">Leading</span><div class="note" style="margin-top:4px">Check-in · ความคืบหน้าโครงการ Q1–Q4 · สายตรงคณบดี · เบิกจ่ายสะสม</div></div>
            <div class="grow"><span class="tag">Lagging</span><div class="note" style="margin-top:4px">มีงานทำ · Scopus/อาจารย์ · พึงพอใจลูกค้า · คงอยู่บุคลากร</div></div>
          </div>
        </div>
        <div class="col" style="flex:0 0 300px;gap:8px">
          <div class="card" style="padding:9px 12px">
            <div class="lbl">KPI 33 ตัว ณ ก.ค. 2569</div>
            <div class="row" style="gap:6px;margin-top:6px;align-items:flex-end">
              <div class="grow" style="text-align:center"><div class="big green" style="font-size:24px">8</div><div class="note" style="font-size:11px">บรรลุ</div></div>
              <div class="grow" style="text-align:center"><div class="big red" style="font-size:24px">5</div><div class="note" style="font-size:11px">ต่ำกว่าเป้า</div></div>
              <div class="grow" style="text-align:center"><div class="big" style="font-size:24px;color:var(--mute)">12</div><div class="note" style="font-size:11px">รอรอบ</div></div>
            </div>
          </div>
          <div class="card k" style="padding:9px 12px;flex:1"><div class="lbl">KM · ธรรมาภิบาลข้อมูล</div><div class="txt" style="font-size:12px;margin-top:3px">คลังหลักฐาน <b>~1,063 รายการ</b> · KM <b>81.25%</b> (เป้า 70) · ประกาศธรรมาภิบาลข้อมูล + BCP · Uptime <b>99.99%</b></div></div>
        </div>
      </div>
    </div>
    <div class="col" style="flex:0 0 250px;gap:8px">
      <div class="card n" style="flex:1;padding:12px 14px">
        <div class="lbl">Result Linkage</div>
        <div class="txt" style="font-size:12.5px;color:#DCE4EE;margin-top:6px">ทุกตัวชี้วัดหมวด 7 ระบุ <b style="color:#fff">กระบวนการต้นทาง</b> · เป้า · แนวโน้ม · คู่เทียบ</div>
        <div style="border-top:1px solid rgba(255,255,255,.18);margin:10px 0"></div>
        <div class="lbl">ทบทวน → ปรับปรุงจริง</div>
        <ul class="b" style="margin-top:6px"><li style="color:#DCE4EE;font-size:12px">Mid-year: มีงานทำต่ำกว่าเป้า → Why-Why → 7 โครงการทักษะแรงงาน</li><li style="color:#DCE4EE;font-size:12px">Annual: กิจกรรมชุมชน 1/5 = ช่องว่างการรายงาน → แก้ Data Dictionary</li></ul>
      </div>
    </div>
  </div>
</section>
'''

S09 = '''<!-- 09 หมวด 5 -->
<section class="s" data-cap="หมวด 5 บุคลากร">
  <div class="head"><div class="eyebrow">หมวด 5 · บุคลากร · จุดเด่นที่กรรมการรับรอง + ระบบที่เพิ่มปี 2568</div><h1 class="t">วางแผนกำลังคนจากขีดความสามารถ × อัตรากำลัง คงอยู่ 100% ลาออกปีแรก 0% และซื่อตรงกับตัวที่ยังต่ำกว่าเป้า</h1><div class="sub">ตาราง 5-1 กำลังคน 6 ขั้น · ตาราง 5-4 การสืบทอดตำแหน่ง · ผลลัพธ์ตาราง 7.3-1</div></div>
  <div class="body row" style="gap:14px">
    <div class="grow col" style="gap:10px">
      <div class="step">
        <div class="st"><div class="num">01</div><div class="nm">Capability (PSF)</div><div class="who">ประธานหลักสูตร · ปี</div></div>
        <div class="st"><div class="num">02</div><div class="nm">Capacity (FTES)</div><div class="who">เลขานุการ · ส่วน จนท.</div></div>
        <div class="st"><div class="num">03</div><div class="nm">คัดกรองคำขออัตรา</div><div class="who">บอร์ด · เกณฑ์ 3 ข้อ</div></div>
        <div class="st"><div class="num">04</div><div class="nm">สรรหา · ค่าย · พี่เลี้ยง</div><div class="who">คณะทำงานบุคลากร</div></div>
        <div class="st"><div class="num">05</div><div class="nm">พัฒนา · e-Portfolio</div><div class="who">ทุก 6 เดือน</div></div>
        <div class="st"><div class="num">06</div><div class="nm">ประเมินความผูกพัน</div><div class="who">สำรวจ · ปีละครั้ง</div></div>
      </div>
      <div class="row" style="gap:10px;flex:1">
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">ผลลัพธ์บุคลากร · ตาราง 7.3-1</div>
          <table class="t" style="font-size:12px;margin-top:4px">
            <tr><th>ตัวชี้วัด</th><th class="n">2566</th><th class="n">2567</th><th class="n">2568</th><th class="n">เป้า</th></tr>
            <tr class="hl"><td>อัตราคงอยู่ (%)</td><td class="n">97.37</td><td class="n">100</td><td class="n">100</td><td class="n">90</td></tr>
            <tr class="hl"><td>ลาออกปีแรก (%)</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">0</td></tr>
            <tr class="hl"><td>ตำแหน่งวิชาการ (%)</td><td class="n">37.50</td><td class="n">53.65</td><td class="n">57.89</td><td class="n">35</td></tr>
            <tr class="hl"><td>อาจารย์ ป.เอก (%)</td><td class="n">79.49</td><td class="n">76.92</td><td class="n">78.94</td><td class="n">78</td></tr>
            <tr><td><span class="red">พัฒนาสมรรถนะ วิชาการ / สนับสนุน (%)</span></td><td class="n">—</td><td class="n">—</td><td class="n red">70.3 / 27.3</td><td class="n">75</td></tr>
            <tr><td><span class="red">PSF/UKPSF สะสม (คน)</span></td><td class="n">—</td><td class="n">—</td><td class="n red">2</td><td class="n">19</td></tr>
          </table>
        </div>
        <div class="col" style="flex:0 0 250px;gap:8px">
          <div class="card k" style="padding:9px 12px;flex:1"><div class="lbl">Learning · ตัวที่ต่ำกว่าเป้า</div><div class="txt" style="font-size:12px;margin-top:3px">PSF 2/19 → ยื่นเป็นรุ่น ผูกงบพัฒนา 6,000 บ./คน กับแผนรายบุคคลใน e-Portfolio · ติดตามในบอร์ดรายเดือน</div></div>
          <div class="card k" style="padding:9px 12px;flex:1"><div class="lbl">การสืบทอดตำแหน่ง</div><div class="txt" style="font-size:12px;margin-top:3px">อายุงาน ≥20 ปี <b>15 คน (31%)</b> · เกษียณ 1 ราย ปี 2569 · ลาศึกษาต่อ 3 · ความเสี่ยงสูงสุดปี 2569 (ปค.5)</div></div>
        </div>
      </div>
    </div>
    <div class="col" style="flex:0 0 270px;gap:8px">
      <div class="ph" style="flex:1 1 0;min-height:0"><img src="img/baisrisukwan.jpg" alt="พิธีบายศรีสู่ขวัญ"><div class="cap">พิธีบายศรีสู่ขวัญ — วัฒนธรรม T.E.A.M. (ก.พ. 2569)</div></div>
      <div class="card n" style="padding:10px 12px"><div class="lbl">ประกาศสิทธิประโยชน์ (ลงนามคณบดี)</div><div class="txt" style="font-size:12px;color:#DCE4EE;margin-top:3px">ค่าตอบแทนวิจัย · ค่าตีพิมพ์ · ค่าเดินทางนำเสนอ · ความผูกพัน <b style="color:#fff">4.69</b> · แผนพัฒนาบุคลากร <b style="color:#fff">4.62</b></div></div>
    </div>
  </div>
</section>
'''

S10 = '''<!-- 10 หมวด 6 -->
<section class="s" data-cap="หมวด 6 การปฏิบัติการ">
  <div class="head"><div class="eyebrow">หมวด 6 · การปฏิบัติการ · Design Cycle · ประสิทธิผลกระบวนการ · ความปลอดภัย</div><h1 class="t">ออกแบบหลักสูตรและบริการจากข้อกำหนดลูกค้า วัดประสิทธิภาพกระบวนการเป็นตัวเลข และปรับปรุงจากผลจริง</h1><div class="sub">Requirement Deployment 5 ขั้น + Design Cycle 6 ขั้น · ตาราง 6.2 ความเสี่ยง 5 ด้าน (S/O/F/C/H)</div></div>
  <div class="body row" style="gap:14px">
    <div class="grow col" style="gap:10px">
      <div class="row" style="gap:10px">
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">Design Cycle ที่ใช้จริงปี 2568</div>
          <ul class="b" style="margin-top:6px;font-size:12.5px">
            <li>ปรับปรุงหลักสูตรครบวงรอบ <b>3 หลักสูตร (MTA · SE · CE)</b> ผู้ทรงคุณวุฒิภายนอก 3–5 ท่าน → สภาฯ อนุมัติ <b>21 ม.ค. 69</b></li>
            <li><b>Non-degree ADT2025</b> Co-Design กับซัมมิท คอมพิวเตอร์ (SFIA) งบภายนอก <b>1.2 ลบ.</b> · รุ่น 1 Job-Ready 65% → รุ่น 2 ปรับ <b>5 มาตรการ</b></li>
          </ul>
        </div>
        <div class="card grow" style="padding:10px 12px">
          <div class="lbl">Learning ระดับกระบวนการ · ซ้อมอพยพ S7</div>
          <div class="row" style="gap:10px;margin-top:8px;align-items:center">
            <div style="text-align:center"><div class="lbl">ก.พ. 2568</div><div class="big red" style="font-size:30px">3.00<small>นาที</small></div><div class="note" style="font-size:11px">ไม่ผ่าน 5 ข้อ</div></div>
            <div class="mono" style="font-size:22px;color:var(--gold)">&rarr;</div>
            <div style="text-align:center"><div class="lbl">ก.พ. 2569</div><div class="big green" style="font-size:30px">1.50<small>นาที</small></div><div class="note" style="font-size:11px">แก้ครบ 5 ข้อ</div></div>
            <div class="txt grow" style="font-size:12px">แก้ที่ critical step: จุดรวมพล · ผู้นำทางรายชั้น · สัญญาณ · ป้าย · การนับคน (จป.วิชาชีพ)</div>
          </div>
        </div>
      </div>
      <div class="row" style="gap:10px;flex:1">
        <div class="card kpi grow k"><div class="lbl">Lean ลดรอบเวลาบริการ</div><div class="big">25.8<small>%</small></div><div class="d">เป้า 25 บรรลุ</div></div>
        <div class="card kpi grow k"><div class="lbl">ครุภัณฑ์ส่งมอบตามข้อกำหนด</div><div class="big">6/6</div><div class="d">ประกาศผู้ส่งมอบ + SLA</div></div>
        <div class="card kpi grow k"><div class="lbl">ทะเบียนความเสี่ยง ปค.4/5</div><div class="big">4 <small>→</small> 7</div><div class="d">2568 กิจกรรม 5/5 · 2569 สูง 1</div></div>
        <div class="card kpi grow k"><div class="lbl">BCP · RTO ระบบ IT</div><div class="big">2<small>ชม.</small></div><div class="d">7 เหตุการณ์ · คณบดีหัวหน้าทีม</div></div>
      </div>
    </div>
    <div class="col" style="flex:0 0 300px;gap:8px">
      <div class="ph" style="flex:1 1 0;min-height:0"><img src="img/mou-healthtech.jpg" alt="พิธีลงนาม MoU กับสมาคมการค้าเฮลท์เทคไทย"><div class="cap">MoU สมาคมการค้าเฮลท์เทคไทย (11 ก.ย. 2569)</div></div>
      <div class="ph" style="flex:1 1 0;min-height:0"><img src="img/iot1.jpg" alt="Workshop IoT Innovation"><div class="cap">Workshop IoT — ห้องปฏิบัติการ S7 (ส.ค. 2569)</div></div>
    </div>
  </div>
</section>
'''

S11 = '''<!-- 11 หมวด 7.1 -->
<section class="s" data-cap="7.1 ผลลัพธ์การเรียนรู้">
  <div class="head"><div class="eyebrow">หมวด 7.1 · ผลลัพธ์การเรียนรู้ · LeTCI · ต้นทาง: หมวด 6.1 / 3.1</div><h1 class="t">ผลงานและรางวัลนักศึกษาสูงกว่าเป้าชัดเจน ภาวะมีงานทำและสำเร็จตามแผนต่ำกว่าเป้าและมีมาตรการกำกับ</h1><div class="sub">แท่งน้ำเงิน = ADT · แท่งเขียว = คู่เทียบ · เส้นประ = ค่าเป้าหมาย · ↑ สูงดี</div></div>
  <div class="body row" style="gap:12px">
    <div class="col" style="flex:0 0 580px;gap:8px">
      <div class="row" style="gap:8px;flex:1">
        <div class="card grow" style="padding:8px 10px 6px"><div class="lbl">มีงานทำใน 1 ปี (%)</div>{{CHART_EMP}}<div class="note" style="font-size:11px">ลด 4 ปี ต่ำกว่า มฟล. → 7 โครงการทักษะแรงงาน 548,200 บ.</div></div>
        <div class="card grow" style="padding:8px 10px 6px"><div class="lbl">สำเร็จตามแผน ป.ตรี (%)</div>{{CHART_GRAD}}<div class="note" style="font-size:11px">บว. 8.33 (เป้า 25 ฐาน 1/12) → ติดตามรายภาค · คงอยู่ 85 / 100</div></div>
      </div>
      <div class="row" style="gap:8px;flex:1">
        <div class="card grow" style="padding:8px 10px 6px"><div class="lbl">ผลงานตีพิมพ์ นศ.บว. (%)</div>{{CHART_PUB}}<div class="note" style="font-size:11px">29 ชิ้น (Scopus 26 · TCI 3) · สอบป้องกันผ่าน 100%</div></div>
        <div class="card grow" style="padding:8px 10px">
          <div class="lbl">Exit Exam 2568 · %S</div>
          <table class="t" style="font-size:11.5px;margin-top:4px">
            <tr><th>วิชา</th><th class="n">%S</th><th class="n">เป้า · คู่เทียบ</th></tr>
            <tr><td>ENG (n=169)</td><td class="n red">14.2</td><td class="n">60 · มฟล. 35.8</td></tr>
            <tr><td>IT (n=24)</td><td class="n">62.5</td><td class="n">60</td></tr>
            <tr><td>GE (n=148)</td><td class="n red">39.2</td><td class="n">60</td></tr>
            <tr><td>MAJOR (n=82)</td><td class="n">61.0</td><td class="n">60</td></tr>
          </table>
          <div class="note" style="font-size:11px;margin-top:4px">ENG → ติวเข้ม + EMI ทุกหลักสูตร</div>
        </div>
      </div>
    </div>
    <div class="grow col" style="gap:8px">
      <div class="row" style="gap:8px;flex:1">
        <div class="ph grow"><img src="img/design-athon.jpg" alt="Physical UI Design-athon 2026"><div class="cap">Grand Prize · PHYSICAL UI DESIGN-ATHON 2026</div></div>
        <div class="ph grow"><img src="img/ted-venture.jpg" alt="TED Venture Catalyst 2026"><div class="cap">ชนะเลิศ Startup Thailand League ภาคเหนือ</div></div>
      </div>
      <div class="row" style="gap:8px;flex:1">
        <div class="ph grow"><img src="img/huawei-ict.jpg" alt="Huawei ICT Competition"><div class="cap">รองอันดับ 2 เอเชีย-แปซิฟิก · Huawei ICT</div></div>
        <div class="col grow" style="gap:8px">
          <div class="card n kpi" style="padding:9px 11px;flex:1"><div class="lbl">รางวัลนักศึกษา 2568</div><div class="big" style="font-size:26px">&ge;8<small style="color:#B9C6D8">รายการ</small></div><div class="d">ระดับชาติ/นานาชาติ</div></div>
          <div class="card n kpi" style="padding:9px 11px;flex:1"><div class="lbl">Outbound · ทักษะอนาคต</div><div class="big" style="font-size:26px">4.23<small style="color:#B9C6D8">% · 4.51</small></div><div class="d">เป้า 3.5 / 4.25 บรรลุ</div></div>
        </div>
      </div>
    </div>
  </div>
</section>
'''

S15 = '''<!-- 15 จุดเด่น / โอกาสในการปรับปรุง -->
<section class="s" data-cap="จุดเด่น · โอกาสในการปรับปรุง · ก้าวต่อไป">
  <div class="head"><div class="eyebrow">การจำลองประเมินตนเอง · จุดเด่นและโอกาสในการปรับปรุง</div><h1 class="t">เรารู้จุดเด่นและช่องว่างของตนเองก่อนวันตรวจ — ทุกช่องว่างมีเจ้าของ กำหนดเวลา และตัวชี้วัด</h1><div class="sub">เป้าผลประเมิน 2568 ไม่ต่ำกว่าระดับ 3 · ตัวชี้วัด มฟล. 5.7 "ผ่าน EdPEx200" · เล่ม SAR 93 หน้า ไม่มีข้อความ "ไม่พบข้อมูล"</div></div>
  <div class="body row" style="gap:12px">
    <div class="card grow" style="padding:10px 12px;border-top:3px solid var(--green)">
      <div class="lbl">จุดเด่น (ยืนยันด้วยตัวเลข)</div>
      <ul class="b" style="margin-top:6px;font-size:12.5px">
        <li><b>บุคลากร:</b> คงอยู่ 100% · ตำแหน่งวิชาการ 57.9% (เป้า 35)</li>
        <li><b>นักศึกษา:</b> ตีพิมพ์ 58% (เป้า 25) · รางวัล ≥8 รายการ</li>
        <li><b>การเงิน/วิจัย:</b> ทุนภายนอก 12.14 ลบ. (เป้า 6.5) · เบิกจ่าย 52.5% vs มฟล. 34.1%</li>
        <li><b>ระบบที่ใช้จริง:</b> สายตรงคณบดี · Check-in · BCP · บอร์ดรายเดือน</li>
        <li><b>คู่เทียบ 3 ระดับ:</b> BI มฟล. · AUN Benchmark · OpenAlex</li>
      </ul>
    </div>
    <div class="card grow" style="padding:10px 12px;border-top:3px solid var(--red);flex:1.3">
      <div class="lbl">โอกาสในการปรับปรุงที่ยังเปิด · เจ้าของ</div>
      <table class="t" style="font-size:12px;margin-top:6px">
        <tr><th>ตัวชี้วัด</th><th class="n">ผล / เป้า</th><th>มาตรการ · ผู้รับผิดชอบ</th></tr>
        <tr><td>มีงานทำ 1 ปี</td><td class="n red">64.5 / 70</td><td>7 โครงการทักษะแรงงาน · กิจการ นศ.</td></tr>
        <tr><td>สำเร็จตามแผน ป.ตรี</td><td class="n red">44.0 / 70</td><td>ติดตามรายภาค · ประธานหลักสูตร</td></tr>
        <tr><td>Exit Exam ENG</td><td class="n red">14.2 / 60</td><td>EMI + ติวเข้ม · คณะทำงานวิชาการ</td></tr>
        <tr><td>PSF สะสม</td><td class="n red">2 / 19</td><td>ยื่นเป็นรุ่น · รองคณบดี</td></tr>
        <tr><td>Scopus/อาจารย์</td><td class="n red">0.58 / 1.5</td><td>ทุนภายใน 1.56 ลบ. · คณะทำงานวิจัย</td></tr>
        <tr><td>พึงพอใจผู้เรียน 6 รายการ</td><td class="n red">3.4–3.9 / 4</td><td>แบบสำรวจใหม่ + PR · คณะทำงาน PR</td></tr>
      </table>
    </div>
    <div class="col" style="flex:0 0 280px;gap:8px">
      <div class="card n" style="flex:1;padding:12px 14px">
        <div class="lbl">ก้าวต่อไป 12 เดือน</div>
        <ul class="b" style="margin-top:6px"><li style="color:#DCE4EE;font-size:12px">ป้อน EdPEx เข้า AUN Benchmark รอบแรก ก.ย. 2569</li><li style="color:#DCE4EE;font-size:12px">สำรวจผู้เรียน/ลูกค้า/บุคลากรฉบับใหม่ครบทุกกลุ่ม</li><li style="color:#DCE4EE;font-size:12px">แผนพัฒนา 2570–2574 + ARIC ระยะที่ 1</li></ul>
      </div>
      <div class="card y" style="padding:10px 12px"><div class="lbl">ขอรับจากคณะกรรมการ</div><div class="txt" style="font-size:12.5px;margin-top:4px">ข้อเสนอแนะต่อ<b>ความเป็นระบบ</b>ของหมวด 4 และ 6 และ<b>คู่เทียบ</b>ที่เลือก</div></div>
    </div>
  </div>
</section>
'''

replace_section("slides_a.html", "03", S03)
replace_section("slides_b.html", "06", S06)
replace_section("slides_b.html", "07", S07)
replace_section("slides_b.html", "08", S08)
replace_section("slides_b.html", "09", S09)
replace_section("slides_b.html", "10", S10)
replace_section("slides_c.html", "11", S11)
replace_section("slides_c.html", "15", S15)
