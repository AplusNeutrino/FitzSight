from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PINNED_SKILL_COMMIT = "c91369c449d34755d320a8b81d0734000d99d1ab"
DEFAULT_SKILL_ROOT = Path.home() / ".codex" / "skills" / "guizang-ppt-skill"


EXTRA_CSS = r"""
<style id="fitzsight-cn-deck">
  .fs-head{display:flex;flex-direction:column;gap:1.2vh;margin-bottom:3vh}
  .fs-title{font-family:var(--sans),var(--sans-zh);font-size:min(5.2vw,9.2vh);line-height:1.04;font-weight:200;letter-spacing:-.035em;color:var(--text-primary)}
  .fs-subtitle{font-family:var(--sans),var(--sans-zh);font-size:max(18px,1.2vw);line-height:1.55;color:var(--text-secondary);font-weight:400;max-width:60ch}
  .fs-kicker{font-family:var(--mono),var(--sans-zh);font-size:14px;letter-spacing:.18em;color:var(--accent);font-weight:600}
  .fs-body{font-family:var(--sans),var(--sans-zh);font-size:max(18px,1.15vw);line-height:1.55;color:var(--text-secondary);font-weight:400}
  .fs-small{font-family:var(--sans),var(--sans-zh);font-size:max(16px,.92vw);line-height:1.5;color:var(--text-secondary);font-weight:500}
  .fs-meta{font-family:var(--mono),var(--sans-zh);font-size:14px;line-height:1.4;letter-spacing:.08em;color:var(--text-helper);font-weight:600}
  .fs-card{border-top:2px solid var(--ink);padding:2.2vh 1.25vw 1.8vh;background:var(--grey-1);min-height:0;overflow:hidden}
  .fs-card.accent-card{border-top-color:var(--accent);background:rgba(var(--accent-rgb),.07)}
  .fs-card h3{font-family:var(--sans),var(--sans-zh);font-size:max(20px,1.45vw);line-height:1.25;font-weight:400;margin-bottom:1.1vh}
  .fs-card p,.fs-card li{font-family:var(--sans),var(--sans-zh);font-size:max(16px,.94vw);line-height:1.5;color:var(--text-secondary);font-weight:500}
  .fs-grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3vw;min-height:0}
  .fs-grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:1.5vw;min-height:0}
  .fs-grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1vw;min-height:0}
  .fs-num{font-family:var(--sans);font-size:min(6.2vw,10.6vh);line-height:.9;font-weight:200;letter-spacing:-.045em;color:var(--accent)}
  .fs-num.dark-num{color:var(--ink)}
  .fs-label{font-family:var(--mono),var(--sans-zh);font-size:14px;line-height:1.35;letter-spacing:.08em;color:var(--text-helper);font-weight:600;margin-top:1vh}
  .fs-timeline{display:grid;grid-template-columns:repeat(7,1fr);gap:.7vw;align-items:stretch}
  .fs-step{border-top:3px solid var(--accent);padding-top:1.4vh;min-height:17vh}
  .fs-step b{display:block;font-family:var(--sans);font-size:min(2.3vw,4vh);font-weight:300;color:var(--accent);margin-bottom:.7vh}
  .fs-step span{font-family:var(--sans),var(--sans-zh);font-size:max(16px,.9vw);line-height:1.45;color:var(--text-secondary);font-weight:500}
  .fs-flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:1vw;align-items:center;min-height:0}
  .fs-layer{border:2px solid var(--ink);padding:2.4vh 1.4vw;min-height:26vh;display:flex;flex-direction:column;justify-content:space-between}
  .fs-layer.accent-layer{border-color:var(--accent);background:var(--accent);color:#fff}
  .fs-arrow{font-size:min(3vw,5vh);font-weight:200;color:var(--accent)}
  .fs-chip{display:inline-flex;align-items:center;padding:.7vh .7vw;border:1px solid var(--border-strong);font-size:max(14px,.78vw);font-weight:600;margin:.25vh .25vw .25vh 0;background:#fff}
  .fs-pill{display:inline-block;border:1px solid var(--accent);color:var(--accent);padding:.65vh .65vw;font-family:var(--mono),var(--sans-zh);font-size:14px;font-weight:600;margin:.25vh .22vw}
  .fs-quote{font-family:var(--sans),var(--sans-zh);font-size:min(4.7vw,8.2vh);line-height:1.08;font-weight:200;letter-spacing:-.035em}
  .fs-accent{color:var(--accent)}
  .fs-rule{height:1px;background:var(--border-strong);margin:1.4vh 0}
  .fs-trace-img{width:100%;height:43vh;object-fit:contain;object-position:center center;background:var(--grey-1);border:1px solid var(--border-subtle)}
  .fs-footer{margin-top:auto;padding-top:1.6vh;border-top:1px solid var(--border-subtle);display:flex;justify-content:space-between;align-items:end}
  .slide.export-static [data-anim]{opacity:1!important;transform:none!important}
</style>
"""


SLIDES = r"""
<section class="slide accent" data-layout="SWISS-COVER-ASCII" data-animate="hero" data-slide-id="cover">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min"><div class="l">FitzSight · GOAI 2026</div><div class="r">AI+金融 · 01 / 12</div></div>
    <div style="flex:1;padding:0;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh;position:relative;z-index:1">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">证据驱动的金融运营调查智能体</div>
      <h1 data-anim="title" style="align-self:center;font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(11.6vw,19vh);line-height:.94;letter-spacing:-.035em;color:#fff">从指标变化<br/>走到<span style="font-style:italic;font-weight:300">可验证证据</span></h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.24);padding-top:2vh">
        <div class="lead" style="max-width:56ch;color:rgba(255,255,255,.9)">FitzSight 把“为什么这个指标变了？”转化为受约束、可复现、可审计的调查闭环。</div>
        <div style="display:flex;justify-content:space-between"><div class="t-meta" style="color:rgba(255,255,255,.64)">自主调查 · 人类决策</div><div class="t-meta" style="color:rgba(255,255,255,.64)">v0.13.0 · 合成数据</div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide split" data-layout="S03" data-animate="statement" data-slide-id="problem">
  <div class="canvas-card"><div class="split-half">
    <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
      <div class="chrome-min"><div class="l">真实问题</div><div class="r">02 / 12</div></div>
      <div><div class="t-meta" style="color:rgba(255,255,255,.72);margin-bottom:2vh">金融运营分析师</div><div class="fs-quote" style="color:#fff">看见了<br/>指标变化，<br/>却仍要手工寻找<span style="font-style:italic">为什么</span>。</div></div>
      <div class="t-meta" style="color:rgba(255,255,255,.64)">Dashboard ≠ 可审计解释</div>
    </div>
    <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
      <div class="chrome-min"><div class="l">手工调查路径</div><div class="r">7 个环节</div></div>
      <div style="display:flex;flex-direction:column;gap:1.7vh">
        <div class="fs-body"><b>01</b> 找表、核对口径、确定时间窗口</div><div class="rule"></div>
        <div class="fs-body"><b>02</b> 下钻维度、做统计检验和贡献分解</div><div class="rule"></div>
        <div class="fs-body"><b>03</b> 查业务事件、对账、写报告</div><div class="rule"></div>
        <div class="fs-body"><b>风险</b> 泛化模型可以更快给出解释，却未必正确、可追溯或知道何时拒绝。</div>
      </div>
      <div class="fs-meta">目标用户：Brokerage / FinTech Operations Analyst</div>
    </div>
  </div></div>
</section>

<section class="slide light" data-layout="S05" data-animate="stack-build" data-slide-id="product">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">产品方案</div><div class="r">03 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">从提问到核验</div><h2 class="fs-title">模型负责规划，工具负责计算，验证器决定能否呈现</h2></div>
    <div class="fs-grid-3" style="flex:1">
      <div class="fs-layer accent-layer"><div class="fs-meta" style="color:rgba(255,255,255,.72)">01 · 规划</div><div><div style="font-size:min(4vw,7vh);font-weight:200">受约束规划</div><p class="fs-small" style="color:rgba(255,255,255,.86);margin-top:2vh">DeepSeek V4 只能描述白名单内的高层调查动作。</p></div><div class="fs-meta" style="color:rgba(255,255,255,.68)">本地意图门控先行</div></div>
      <div class="fs-layer"><div class="fs-meta">02 · 计算</div><div><div style="font-size:min(4vw,7vh);font-weight:200">确定性计算</div><p class="fs-small" style="margin-top:2vh">只读 SQL、统计检验、异常检测与贡献分解拥有所有关键数字。</p></div><div class="fs-meta">不允许模型生成 SQL</div></div>
      <div class="fs-layer"><div class="fs-meta">03 · 核验</div><div><div style="font-size:min(4vw,7vh);font-weight:200">证据核验</div><p class="fs-small" style="margin-top:2vh">每条重要结论必须绑定 Evidence ID；核验失败即停止输出。</p></div><div class="fs-meta">核验失败即关闭</div></div>
    </div>
    <div class="fs-footer"><span class="fs-meta">不是“和 CSV 聊天”</span><span class="fs-meta">可检查 · 可质疑 · 可拒绝</span></div>
  </div>
</section>

<section class="slide light" data-layout="S11" data-animate="timeline-walk" data-slide-id="loop">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">任务闭环</div><div class="r">04 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">智能体任务闭环</div><h2 class="fs-title">从业务问题到有边界的答案</h2><p class="fs-subtitle">每一步都有明确输入、批准能力、失败处理和证据出口。</p></div>
    <div class="fs-timeline" style="flex:1;align-content:center">
      <div class="fs-step"><b>01</b><span>用户问题<br/>明确指标与范围</span></div>
      <div class="fs-step"><b>02</b><span>意图门控<br/>越界问题先拒绝</span></div>
      <div class="fs-step"><b>03</b><span>受限计划<br/>固定动作序列</span></div>
      <div class="fs-step"><b>04</b><span>工具调用<br/>只读确定性计算</span></div>
      <div class="fs-step"><b>05</b><span>证据登记<br/>追加式 Evidence</span></div>
      <div class="fs-step"><b>06</b><span>结论核验<br/>覆盖与边界检查</span></div>
      <div class="fs-step"><b>07</b><span>结果交付<br/>支持、假设或拒绝</span></div>
    </div>
    <div class="fs-footer"><span class="fs-meta">缺失信息 / 工具失败 / 因果不足均有显式分支</span><span class="fs-meta">人工确认</span></div>
  </div>
</section>

<section class="slide light" data-layout="S17" data-animate="system-diagram" data-slide-id="architecture">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">系统架构</div><div class="r">05 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">DEEPSEEK V4 · 受限设计</div><h2 class="fs-title">三层分权，而不是把所有权限交给模型</h2></div>
    <div class="fs-flow" style="flex:1">
      <div class="fs-layer accent-layer"><div class="fs-meta" style="color:rgba(255,255,255,.7)">规划层</div><div><h3 style="font-size:min(3.4vw,5.8vh);font-weight:200">DeepSeek V4</h3><p class="fs-small" style="color:rgba(255,255,255,.86);margin-top:1.5vh">Flash 默认，Pro 可切换；JSON Output；思考模式关闭。</p></div><div class="fs-meta" style="color:rgba(255,255,255,.7)">仅批准动作名称与目的</div></div>
      <div class="fs-arrow">→</div>
      <div class="fs-layer"><div class="fs-meta">执行层</div><div><h3 style="font-size:min(3.4vw,5.8vh);font-weight:200">确定性工具</h3><div style="margin-top:1.5vh"><span class="fs-chip">只读 SQL</span><span class="fs-chip">统计检验</span><span class="fs-chip">贡献分解</span><span class="fs-chip">异常检测</span></div></div><div class="fs-meta">关键数值不由模型计算</div></div>
      <div class="fs-arrow">→</div>
      <div class="fs-layer"><div class="fs-meta">核验层</div><div><h3 style="font-size:min(3.4vw,5.8vh);font-weight:200">EvidenceClaimVerifier</h3><p class="fs-small" style="margin-top:1.5vh">验证证据覆盖、因果措辞、禁止字段与安全边界。</p></div><div class="fs-meta">核验失败即关闭 · 只输出已核验答案</div></div>
    </div>
  </div>
</section>

<section class="slide light" data-layout="S06" data-animate="measure-up" data-slide-id="hero-findings">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">核心案例 · 欧洲 FTD</div><div class="r">06 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">问题：7 月 15 日后欧洲 FTD 转化为何恶化？</div><h2 class="fs-title">测量变化，也测量解释的可信边界</h2></div>
    <div class="fs-grid-4" style="flex:1;align-items:end">
      <div class="fs-card accent-card" style="height:34vh"><div class="fs-num">-7.53</div><div class="fs-label">百分点 · 受影响团队转化变化</div><p style="margin-top:2vh">23.37% → 15.84%<br/>p = 0.00235</p></div>
      <div class="fs-card" style="height:29vh"><div class="fs-num dark-num">-1.21</div><div class="fs-label">百分点 · 欧洲控制组变化</div><p style="margin-top:2vh">对照组变化明显更小</p></div>
      <div class="fs-card accent-card" style="height:39vh"><div class="fs-num">+29.15</div><div class="fs-label">分钟 · 响应时间中位数变化</div><p style="margin-top:2vh">94.30 → 123.45<br/>p &lt; 0.001</p></div>
      <div class="fs-card" style="height:25vh"><div class="fs-num dark-num">8/27</div><div class="fs-label">变更后每日延迟异常</div><p style="margin-top:2vh">Team A 为最大负向贡献团队</p></div>
    </div>
    <div class="fs-footer"><span class="fs-meta">合成数据 · seed 20260811 · SQLite</span><span class="fs-meta">候选根因 ≠ 已证明现实因果</span></div>
  </div>
</section>

<section class="slide light" data-layout="S15" data-animate="matrix-fill" data-slide-id="evidence-trace">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">调查轨迹</div><div class="r">07 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">运行时生成的证据</div><h2 class="fs-title" style="font-size:min(4.6vw,8.2vh)">九个批准步骤，每一步都留下 Evidence ID</h2></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:.8vw;flex:1;min-height:0">
      <div class="fs-card accent-card"><h3>01 · 检查字段</h3><p>确认运营字段，不读取评测真值。<br/><b>E0002</b></p></div>
      <div class="fs-card"><h3>02 · 受影响组</h3><p>测量 Team A+B 转化与响应时间。<br/><b>E0003</b></p></div>
      <div class="fs-card"><h3>03 · 控制组</h3><p>测量其他欧洲团队的同期变化。<br/><b>E0004</b></p></div>
      <div class="fs-card"><h3>04 · 统计检验</h3><p>验证转化与延迟变化是否显著。<br/><b>E0005–E0006</b></p></div>
      <div class="fs-card accent-card"><h3>05 · 贡献分解</h3><p>Team A 为最大负向贡献团队。<br/><b>E0009–E0010</b></p></div>
      <div class="fs-card"><h3>06 · 异常扫描</h3><p>27 个变更后日期中发现 8 个异常。<br/><b>E0011–E0012</b></p></div>
      <div class="fs-card"><h3>07 · 事件检查</h3><p>识别附近 CRM 路由变更。<br/><b>E0013</b></p></div>
      <div class="fs-card accent-card"><h3>08 · 文档证据</h3><p>定位 CRM-CHANGE-2026-0715#p1。<br/><b>E0014</b></p></div>
      <div class="fs-card"><h3>09 · 证据边界</h3><p>重要结论 6/6 核验通过，保留因果护栏。</p></div>
    </div>
  </div>
</section>

<section class="slide light" data-layout="S04" data-animate="grid-reveal" data-slide-id="intents">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">复用能力</div><div class="r">08 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">封闭能力目录</div><h2 class="fs-title">五类受限意图，覆盖核心金融运营调查</h2></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:1vw;flex:1">
      <div class="fs-card accent-card"><h3>01 · CRM / FTD</h3><p>转化恶化、响应延迟、团队贡献与业务事件。</p></div>
      <div class="fs-card"><h3>02 · 净入金</h3><p>入金、出金与集中度变化的可解释调查。</p></div>
      <div class="fs-card"><h3>03 · 客户智能</h3><p>行为价值分层，仅作描述性决策支持。</p></div>
      <div class="fs-card"><h3>04 · 营销质量</h3><p>线索数量与实际转化质量的拆解。</p></div>
      <div class="fs-card accent-card"><h3>05 · 伪相关排除</h3><p>附近事件存在时，拒绝无证据因果故事。</p></div>
      <div class="fs-card"><h3>边界 · 非聊天机器人</h3><p>目录外问题先拒绝；不允许任意工具或任意动作。</p></div>
    </div>
  </div>
</section>

<section class="slide light" data-layout="S16" data-animate="field-notes" data-slide-id="experience">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">产品体验</div><div class="r">09 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">失败也是明确的产品状态</div><h2 class="fs-title">不确定、失败和越界，都被清楚地呈现</h2></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:1vw;flex:1">
      <div class="fs-card"><h3>结构化输入</h3><p>预设任务与自定义问题共用同一意图门控。</p></div>
      <div class="fs-card accent-card"><h3>运行中可见</h3><p>计划、动作、状态、Evidence ID 形成完整轨迹。</p></div>
      <div class="fs-card"><h3>输出可追溯</h3><p>KPI、图表和发现均来自已核验调查结果。</p></div>
      <div class="fs-card"><h3>工具失败</h3><p>写入错误 Evidence，不补写不存在的文档依据。</p></div>
      <div class="fs-card accent-card"><h3>证据不足</h3><p>返回 insufficient_evidence，而不是完成因果故事。</p></div>
      <div class="fs-card"><h3>人工确认</h3><p>系统提供分析支持，不替代授权人员的最终判断。</p></div>
    </div>
  </div>
</section>

<section class="slide light" data-layout="S19" data-animate="four-cards" data-slide-id="compliance">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">数据、隐私与金融边界</div><div class="r">10 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">以范围边界保障安全</div><h2 class="fs-title">只在可授权、可解释、可回退的范围内工作</h2></div>
    <div class="fs-grid-4" style="flex:1">
      <div class="fs-card accent-card"><div class="fs-num" style="font-size:min(4.8vw,8.4vh)">01</div><h3>合成数据</h3><p>无真实客户 PII、雇主机密或未授权业务数据。</p></div>
      <div class="fs-card"><div class="fs-num dark-num" style="font-size:min(4.8vw,8.4vh)">02</div><h3>只读分析</h3><p>不交易、不转账、不冻结账户，不写入业务系统。</p></div>
      <div class="fs-card"><div class="fs-num dark-num" style="font-size:min(4.8vw,8.4vh)">03</div><h3>不替代专业决策</h3><p>不提供投资建议、授信、AML 或适当性结论。</p></div>
      <div class="fs-card accent-card"><div class="fs-num" style="font-size:min(4.8vw,8.4vh)">04</div><h3>证据优先</h3><p>重要结论必须可定位、可复算、可拒绝。</p></div>
    </div>
    <div class="fs-footer"><span class="fs-meta">生产环境 RBAC / PII / 留存策略属于后续蓝图</span><span class="fs-meta">POC 边界明确披露</span></div>
  </div>
</section>

<section class="slide light" data-layout="S21" data-animate="tech-spec" data-slide-id="evidence">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">工程与开放复用</div><div class="r">11 / 12</div></div>
    <div class="fs-head"><div class="fs-kicker">可复现发布</div><h2 class="fs-title">用测试、评测和离线回退证明“可运行”</h2></div>
    <div style="display:grid;grid-template-columns:1.1fr 1fr;gap:2vw;flex:1;min-height:0">
      <div class="fs-card accent-card" style="display:grid;grid-template-rows:auto 1fr auto">
        <div class="fs-meta">评测结果</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4vw;align-content:center">
          <div><div class="fs-num">5/5</div><div class="fs-label">固定闭环基准通过</div></div>
          <div><div class="fs-num">8/8</div><div class="fs-label">对抗安全案例通过</div></div>
          <div><div class="fs-num">100%</div><div class="fs-label">留出集路由与核验</div></div>
          <div><div class="fs-num">0%</div><div class="fs-label">完整系统危险答案率</div></div>
        </div>
        <div class="fs-meta">受控消融：移除验证门后，危险答案率升至 100%</div>
      </div>
      <div style="display:grid;grid-template-rows:repeat(4,1fr);border-top:2px solid var(--ink)">
        <div style="display:grid;grid-template-columns:9vw 1fr;align-items:center;border-bottom:1px solid var(--border-subtle)"><div class="fs-meta">代码</div><div class="fs-body">MIT License · 公共仓库 · 合成数据生成器</div></div>
        <div style="display:grid;grid-template-columns:9vw 1fr;align-items:center;border-bottom:1px solid var(--border-subtle)"><div class="fs-meta">运行</div><div class="fs-body">SQLite / DuckDB · Streamlit · 离线 HTML / 视频</div></div>
        <div style="display:grid;grid-template-columns:9vw 1fr;align-items:center;border-bottom:1px solid var(--border-subtle)"><div class="fs-meta">模型</div><div class="fs-body">DeepSeek V4 Flash 默认，Pro 可切换；本轮仅 Mock</div></div>
        <div style="display:grid;grid-template-columns:9vw 1fr;align-items:center"><div class="fs-meta">复现</div><div class="fs-body">测试目录、评测目录、运行证据与部署文档齐备</div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide split" data-layout="SWISS-CLOSING-ASCII" data-animate="split-statement" data-slide-id="closing">
  <div class="canvas-card"><div class="split-half">
    <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
      <canvas class="ascii-bg" aria-hidden="true"></canvas>
      <div class="chrome-min" style="position:relative;z-index:1"><div class="l">12 / 12</div><div class="r">FITZSIGHT</div></div>
      <div style="position:relative;z-index:1"><div class="t-meta" style="color:rgba(255,255,255,.72);margin-bottom:2vh">结语</div><h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(8vw,14vh);line-height:.96;font-weight:200;color:#fff">让每个“为什么”<br/>都有可检查的<span style="font-style:italic;font-weight:300">证据边界</span>。</h2></div>
      <div class="t-meta" style="position:relative;z-index:1;color:rgba(255,255,255,.64)">github.com/AplusNeutrino/FitzSight</div>
    </div>
    <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between">
      <div class="chrome-min"><div class="l">下一步</div><div class="r">v0.13.0</div></div>
      <div style="display:flex;flex-direction:column">
        <div style="padding:2.5vh 0;border-top:1px solid var(--border-subtle)"><div class="fs-num dark-num" style="font-size:min(4.4vw,7.8vh)">01</div><h3 class="fs-body" style="font-size:max(20px,1.4vw)">完成真实用户试点与反馈闭环</h3></div>
        <div style="padding:2.5vh 0;border-top:1px solid var(--border-subtle)"><div class="fs-num dark-num" style="font-size:min(4.4vw,7.8vh)">02</div><h3 class="fs-body" style="font-size:max(20px,1.4vw)">补充生产权限、脱敏和留存控制</h3></div>
        <div style="padding:2.5vh 0;border-top:1px solid var(--accent);border-bottom:2px solid var(--accent)"><div class="fs-num" style="font-size:min(4.4vw,7.8vh)">03</div><h3 class="fs-body fs-accent" style="font-size:max(20px,1.4vw)">从初赛方案走向可部署金融运营智能体</h3></div>
      </div>
      <div class="fs-meta" style="text-align:right">自主调查 · 人类决策</div>
    </div>
  </div></div>
</section>
"""


SPEAKER_NOTES = r"""const SPEAKER_NOTES = [
  {id:'cover',title:'从指标变化走到可验证证据',section:'开场',minutes:0.5,purpose:'建立产品定位',talk:['用“看见变化却难以解释”引出痛点','强调证据驱动而非泛聊天','说明全场只讲一个主案例'],transition:'进入分析师的真实工作阻力'},
  {id:'problem',title:'真实问题',section:'场景',minutes:0.7,purpose:'说明用户与痛点',talk:['金融团队已有 BI 和 SQL','困难在跨表调查与可信解释','泛化模型的速度不等于审计性'],transition:'从问题转向产品分权设计'},
  {id:'product',title:'产品方案',section:'方案',minutes:0.7,purpose:'说明核心机制',talk:['模型只做受限规划','数字全部来自确定性工具','验证器掌握答案出口'],transition:'展开完整 Agent 闭环'},
  {id:'loop',title:'任务闭环',section:'方案',minutes:0.8,purpose:'证明不是单轮问答',talk:['按七个阶段讲完整输入到输出','强调失败与证据出口','人工确认保留最终权力'],transition:'解释三层架构如何支撑闭环'},
  {id:'architecture',title:'系统架构',section:'技术',minutes:0.8,purpose:'解释技术分权',talk:['DeepSeek V4 只产生 JSON 计划','SQL 与统计工具拥有数字','EvidenceClaimVerifier 失败即关闭输出'],transition:'用欧洲 FTD 数据展示结果'},
  {id:'hero-findings',title:'核心案例结果',section:'演示',minutes:0.8,purpose:'展示可验证业务发现',talk:['先讲受影响组和控制组差异','再讲响应延迟与异常日','根因只表述为支持候选'],transition:'展示运行轨迹与证据链'},
  {id:'evidence-trace',title:'调查轨迹',section:'演示',minutes:0.7,purpose:'证明过程可审计',talk:['九步均来自批准目录','展示 Evidence ID 与文档段落定位','核验通过仍保留因果护栏'],transition:'从主案例扩展到五类意图'},
  {id:'intents',title:'五类受限意图',section:'复用',minutes:0.6,purpose:'说明可复用价值',talk:['主叙事仍是 CRM/FTD','其余四类证明架构复用','目录外问题不会任意扩展工具'],transition:'说明产品如何处理失败与不确定'},
  {id:'experience',title:'产品体验',section:'体验',minutes:0.6,purpose:'展示异常与人工确认',talk:['运行轨迹对用户可见','工具失败写错误证据','证据不足明确返回而不补故事'],transition:'进入金融安全与数据边界'},
  {id:'compliance',title:'合规边界',section:'安全',minutes:0.7,purpose:'对齐金融赛题边界',talk:['仅使用合成数据','不执行任何高影响动作','生产控制不冒充当前 PoC 能力'],transition:'用工程证据证明可复现'},
  {id:'evidence',title:'工程与开放复用',section:'证据',minutes:0.7,purpose:'总结评测和开源价值',talk:['5/5 固定基准与 8/8 对抗门','解释验证门消融结果','DeepSeek 本轮只做 Mock 不声称在线数据'],transition:'收束到下一步'},
  {id:'closing',title:'证据边界',section:'收束',minutes:0.5,purpose:'留下可记忆结论',talk:['回扣“为什么”问题','重申自主调查与人类决策','邀请评委查看仓库和运行证据'],transition:'结束并进入提问'}
];"""


def build_deck(skill_root: Path, output: Path) -> dict[str, object]:
    template = skill_root / "assets" / "template-swiss.html"
    if not template.exists():
        raise FileNotFoundError(f"guizang-ppt-skill template not found: {template}")
    text = template.read_text(encoding="utf-8")
    text = text.replace(
        "<title>[必填] 替换为 PPT 标题 · Deck Title</title>",
        "<title>FitzSight · GOAI 初赛方案</title>",
    )
    text = text.replace("</head>", EXTRA_CSS + "\n</head>", 1)

    start = '<section class="slide accent" data-animate="hero" data-slide-id="cover">'
    end = "</section>\n\n</div>\n\n<div id=\"nav\"></div>"
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len("</section>")
    text = text[:start_index] + SLIDES.strip() + text[end_index:]

    notes_start = text.index("const SPEAKER_NOTES = [")
    notes_end = text.index("];\nwindow.__SPEAKER_NOTES__", notes_start) + 2
    text = text[:notes_start] + SPEAKER_NOTES + text[notes_end:]
    if "[必填]" in text:
        raise RuntimeError("Deck still contains required placeholders")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    build_info = {
        "product": "FitzSight",
        "version": "0.13.0",
        "language": "zh-CN",
        "pages": 12,
        "style": "guizang-ppt-skill Style B Swiss / IKB",
        "skill_repository": "https://github.com/op7418/guizang-ppt-skill",
        "skill_commit": PINNED_SKILL_COMMIT,
        "skill_license": "AGPL-3.0",
        "deepseek_live": "not_requested",
    }
    (output.parent / "BUILD_INFO.json").write_text(
        json.dumps(build_info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"output": str(output), **build_info}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Chinese GOAI HTML deck from guizang-ppt-skill.")
    parser.add_argument(
        "--skill-root",
        default=os.getenv("GUIZANG_PPT_SKILL_ROOT", str(DEFAULT_SKILL_ROOT)),
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "submission" / "deck-cn" / "index.html"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_deck(Path(args.skill_root), Path(args.output))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
