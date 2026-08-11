# مشروع Track C (Hybrid): توليد متاهة بالـ GA + حلها بـ A*

هذا مشروع نهائي لفكرة Hybrid:
- **Genetic Algorithm (GA)** يتعلّم (يُطوّر) معاملات توليد المتاهة
- ثم **A\*** يحل المتاهة ويعطي قياسات (طول المسار + عدد العقد التي توسّعها A* …)
- هذه القياسات تُستخدم كـ **Fitness** داخل الـ GA لصناعة متاهات أصعب

## المتطلبات
- Python 3.9+
- المكتبات:
  - numpy
  - matplotlib

تثبيت:
```bash
pip install -r requirements.txt
```

## التشغيل
مثال:
```bash
python main.py --size 31 --pop 40 --gens 50 --seed 1234 --out outputs
```

سينتج داخل مجلد `outputs/`:
- `best_maze.png` : صورة المتاهة
- `best_maze_solution.png` : المتاهة + مسار A*
- `fitness_curve.png` : رسم بياني للتطور عبر الأجيال
- `history.csv` / `history.json` : سجل النتائج لكل جيل
- `best_genome.json` : أفضل معاملات (Genome)
- `best_stats.json` : إحصائيات أفضل متاهة

## شرح الجينوم (Genome)
كل فرد في الـ GA يحتوي:
- `corridor_bias` : الميل للاستمرار بنفس الاتجاه أثناء الحفر (ممرات مستقيمة أكثر)
- `goal_bias` : الميل للحفر باتجاه الهدف (عادة يُسهّل المتاهة)
- `loopiness` : نسبة إزالة جدران إضافية لعمل حلقات/مسارات بديلة
- `seed` : رقم عشوائي ثابت لتوليد متاهة قابلة لإعادة الإنتاج

## كيف نحسب الـ Fitness؟
نستخدم مخرجات A* + خصائص المتاهة:
- طول المسار (path length)
- عدد expanded nodes (كم عقدة A* وسّعها)
- عدد النهايات المسدودة (dead ends)
- نسبة الجدران (wall ratio) مع عقوبة إذا خرجت عن نطاق مناسب

> يمكنك تعديل الأوزان داخل `src/ga.py` حسب ما تراه مناسباً للتجارب.
## تشغيل على الويب (Flask)
تمت إضافة ملف **app.py** + قوالب HTML داخل `templates/` لتشغيل المشروع كواجهة ويب.

### التثبيت
```bash
pip install -r requirements.txt
```

### التشغيل
من داخل مجلد المشروع (نفس مكان `app.py`):
```bash
python app.py
```

ثم افتح المتصفح على:
- `http://127.0.0.1:5000`

### ماذا ستجد في الواجهة؟
- **تشغيل GA** بمدخلات (size / population / generations / mutation …) ثم عرض:
  - أفضل متاهة + مسار A*
  - رسم تطور الـ Fitness عبر الأجيال
  - ملفات JSON/CSV للنتائج
- **توليد متاهة واحدة** بمدخلات Genome يدويًا (corridor_bias / goal_bias / loopiness / seed) ثم عرض المتاهة ومسار A*.

> سيتم حفظ مخرجات كل تشغيل داخل مجلد `web_outputs/` بشكل تلقائي (Run ID منفصل لكل تشغيل).

## Author

**Ammar Aikan** — Cybersecurity Student & Security Researcher

## Rights

© 2026 Ammar Aikan. All Rights Reserved. See [COPYRIGHT.md](COPYRIGHT.md).
