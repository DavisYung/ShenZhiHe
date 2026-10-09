# 高频考点重做 · 已完成（2012–2023 卷一+卷二）

## 结果
- 40 份映射产出（12 年 × 甲部/乙部/卷二，2020–2023 乙部各拆 a/b 两段）全部校验通过
- 合并：+1573 点-年 / +2017 sample / +1983 字眼；去重清理 13 条旧双风格重复 sample
- hot.json：**531 个被考知识点（原 251）· 2010 次命中 · 167 必考（原 3）· 250 常考 · 2400 字眼**
- 数据带考标覆盖率：653 点中 531 个（81%）
- 站点：神智核 V0.0.16（4.9MB）已重建，gh-pages 已同步
- 回归测试 6/6 通过（_t_logic / _t_v015 / _t_dwell / _t_settings / _t_backup / _t_imgs）
- 截图验收：高频考点页、课题页（虚拟滚动+考点徽章）渲染正常

## 关键经验
- 子代理整年任务会爆上下文（8/8 全灭）→ 拆成「甲部/乙部/卷二」三份后成功率大增
- 乙部整年任务遇服务端 failed → 再拆「前 6 题/后 6 题」两段后成功
- 子代理禁止整档 read 52KB catalog，必须 grep 过滤
- 旧数据有「有年份无例题」情况：dedup 时不能拿 samples 反推 years
- 旧数据同题存在双 ref 风格（2020-P1-A-20 vs 2020-p1-Q20）：合并后需归一化去重
- 合并后若有子代理延迟重写产出，必须重新合并该档（本次 2023_p1b_b 补合并 +35 字眼）

## 产物
- 数据：f6chem/data/chem/*.json（exam 字段）
- 报告：f6chem/extras/chem/hot.json（由 f6chem/_mk_hot.py 重生）
- 站点：f6chem/site/神智核-V0.0.16.html、神智核.html、f6chem/gh-pages/index.html
- 管线：scratch/ocr_papers.py → prompts2/ → map/ → merge_exam.py → dedup_samples.py → _mk_hot.py
- 备份：scratch/backup_data_premerge/（合并前）、scratch/backup_dedup/、scratch/backup_hot_old.json

## 已完成
- OCR 全部 36 份：pp/<年>_p1.txt / _p2.txt / _ms.txt（RapidOCR，scratch/ocr_papers.py）
- 切分：pp/<年>_p1_mc.txt（甲部）、<年>_p1_b.txt（乙部）、<年>_ms_p1.txt、<年>_ms_p2.txt
- catalog.tsv（653 点）、existing.json、existing_qnums.json（旧标注按年题号：各年 1-24 等）
- 关键结构情报：卷一甲部 = 36 道选择（旧数据只标了 1-24，25-36 待补）；卷二 = 甲/乙/丙三大题、
  题号 1/2/3 连续；2012/2013 是旧纲要，部分题无对应点（写 points:[]）。
- 任务书：scratch/prompts2/<年>_<part>.txt（p1a/p1b/p2 三类，共 36 份；整年任务 8/8 爆上下文后改拆分版）
- 校验 validate_maps.py、合并 merge_exam.py、审计 audit_post.py、报告重生 _mk_hot.py 均就绪
- norm_key 单测通过（scratch/_test_normkey.py）

## 子代理批次（全部任务已发出）
- ✅ p1a 12/12、p2 12/12
- ✅ p1b 完成 10 年：2012–2019（整年档）+ 2020/2021（各拆 a/b 两段）
- [进行中] p1b 2022 两段（a/b）+ 2023 两段（a/b）
- 说明：2020–2023 乙部原整年任务遭遇服务端 failed（零产出），改「前 6 题 / 后 6 题」两段拆分后成功
- ✅ 沙盒预演全链路通过（_t_merge_real.py + _t_mkhotsb.py）
- 校验器放宽：kw 允许方程/数值/单字 ≤40 字；纯图题 kw 允许空列表；支持分段档名 _p1b_a/_p1b_b

## 收尾步骤（全部 map 齐后）
1. python scratch/validate_maps.py（全绿才合并）
2. python scratch/merge_exam.py（备份进 scratch/backup_exam/）
3. python scratch/audit_post.py（新增统计 + 重复检测 + 抽查）
4. python f6chem/_mk_hot.py（重生 extras/chem/hot.json）
5. python f6chem/site/build.py（V0.0.16）
6. 回归：site/_t_logic.py、_t_v015.py、_t_dwell.py、_t_settings.py、_t_backup.py、_t_imgs.py；
   _shot.py "#/chem/extras/hot" 截图验收
