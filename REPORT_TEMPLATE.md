# تقرير مشروع الذكاء الاصطناعي (2–3 صفحات)

## 1) وصف المشكلة والأهداف (Problem & Goals)
**المشكلة:**  
نريد توليد متاهات Grid بحيث تكون:
1) قابلة للحل من نقطة البداية إلى الهدف  
2) “صعبة” من ناحية البحث (المسار أطول / تفرعات أكثر / مجهود أكبر لخوارزمية البحث)

**الأهداف:**
- استخدام مشروع Hybrid: **GA + Search**
- GA يطوّر معاملات توليد المتاهة
- A* يحل المتاهة ويُستخدم لتقييم الصعوبة

## 2) التقنية المختارة (Chosen Technique)
اخترنا **Track C (Hybrid)**:
- **Search:** خوارزمية A* لإيجاد أقصر مسار
- **GA:** لتطوير معاملات توليد المتاهة بحيث تزيد الصعوبة

## 3) تصميم الخوارزميات (Algorithm Design)

### 3.1 توليد المتاهة (Maze Generator)
- تم توليد متاهة باستخدام DFS carving (perfect maze)
- التحكم في شكل المتاهة يتم عبر معاملات (Genome):
  - corridor_bias
  - goal_bias
  - loopiness
  - seed

**مخرجات المولد:** Grid (0 مسار، 1 جدار) مع start و goal.

### 3.2 خوارزمية A* (Search)
- الحالة: خلية (r,c)
- الأفعال: أعلى/أسفل/يمين/يسار
- التكلفة: 1 لكل حركة
- heuristic: Manhattan distance
- المخرجات: المسار + عدد expanded nodes + زمن التنفيذ

### 3.3 الخوارزمية الجينية GA
- **Representation:** Genome = 4 جينات (floats + seed)
- **Selection:** Tournament selection
- **Crossover:** Uniform crossover
- **Mutation:** Gaussian noise للـ floats + تغيير seed
- **Elitism:** الاحتفاظ بأفضل أفراد

### 3.4 دالة الملاءمة Fitness
نُعرّف الصعوبة عبر:
- طول مسار الحل (L)
- عدد expanded nodes (E)
- عدد النهايات المسدودة (D)
- عقوبة لانحراف نسبة الجدران عن قيمة مستهدفة

(اكتب الصيغة التي استخدمتها والأوزان)

## 4) التجارب والنتائج (Experiments & Results)
### إعدادات التجربة
- حجم المتاهة: (مثال 31×31)
- Population size: (مثال 40)
- Generations: (مثال 50)
- معدلات mutation/elitism…

### النتائج
- ضع صور:
  - متاهة عشوائية (جيل 0 أو فرد عشوائي)
  - أفضل متاهة بعد GA
  - أفضل متاهة مع مسار A*

- ضع رسوم بيانية:
  - Best fitness per generation
  - Average fitness per generation
  - (اختياري) expanded nodes أو path length عبر الأجيال

### مناقشة
- لماذا تحسنت النتائج؟
- ما تأثير corridor_bias / goal_bias / loopiness؟
- ما القيود؟ وكيف يمكن تحسين المشروع؟

## 5) خاتمة
خلاصة قصيرة تربط بين GA و A* ولماذا المشروع Hybrid ناجح.
