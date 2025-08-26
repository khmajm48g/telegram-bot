import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive  # استيراد keep_alive

TOKEN = "8029379653:AAEbOr4JLYD2whl--LSCwF8VzqddT_fLwhQ"

# دالة قراءة البيانات من ملف CSV
def read_employee_data():
    employees = {}
    try:
        with open('employee_data (2).csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # التأكد من أن الصف غير فارغ
                    employee_id = row[0].strip()  # الرقم الوظيفي في العمود الأول
                    salary = row[1].strip()  # القيمة المالية في العمود الثاني
                    if employee_id in employees:
                        employees[employee_id].append(salary)  # إضافة القيمة الجديدة للقائمة
                    else:
                        employees[employee_id] = [salary]  # إذا لم يكن الرقم موجوداً بعد
                    print(f"تم تحميل الرقم الوظيفي: {employee_id} مع القيمة المالية: {salary}")
    except FileNotFoundError:
        print("لم يتم العثور على الملف.")
    return employees

# دالة لعرض الفروع مع تسميات صحيحة
async def branches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("الإدارة العامة", callback_data='الإدارة العامة')],
        [InlineKeyboardButton("فرع طرابلس", callback_data='فرع طرابلس')],
        [InlineKeyboardButton("فرع بنغازي", callback_data='فرع بنغازي')],
        [InlineKeyboardButton("فرع سبها", callback_data='فرع سبها')],
        [InlineKeyboardButton("فرع الوسطى", callback_data='فرع الوسطى')],
        [InlineKeyboardButton("فرع الجبل الغربي", callback_data='فرع الجبل الغربي')],
        [InlineKeyboardButton("فرع الجبل الاخضر", callback_data='فرع الجبل الاخضر')],
        [InlineKeyboardButton("فرع الزاوية", callback_data='فرع الزاوية')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('مرحبا، يرجى اختيار الفرع:', reply_markup=reply_markup)

# دالة للتعامل مع اختيار الفرع
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_branch = query.data
    context.user_data['selected_branch'] = selected_branch  # تخزين الفرع المختار في السياق

    # بعد اختيار الفرع، نطلب الرقم الوظيفي
    await query.edit_message_text(text=f"لقد اخترت {selected_branch}. الرجاء إرسال الرقم الوظيفي.")

# دالة لاستقبال الرقم الوظيفي
async def get_salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    employee_id = update.message.text.strip()
    print(f"الرقم الوظيفي الذي أدخلته: {employee_id}")

    # قراءة البيانات من ملف CSV
    employees = read_employee_data()

    # التحقق من الرقم الوظيفي
    if employee_id in employees:
        salary_list = employees[employee_id]
        branch = context.user_data.get('selected_branch', 'لم يتم اختيار الفرع')  # تأكد من أن الفرع تم اختياره
        if branch == 'لم يتم اختيار الفرع':
            await update.message.reply_text("يجب أولاً اختيار الفرع قبل إدخال الرقم الوظيفي.")
        else:
            # تنسيق القيم المالية لعرضها بنقاط
            salary_message = f"تم تسجيل رقم الموظف {employee_id} للفرع: {branch}\n\nالقيم المالية:\n"
            for salary in salary_list:
                salary_message += f" - 💵 `{salary} د.ل`\n"

            salary_message += "\n🎉 **تمت العملية بنجاح!** ✅"
            await update.message.reply_text(salary_message)
    else:
        await update.message.reply_text(f"❌ **لم يتم العثور على الموظف برقم** `{employee_id}`.")

# دالة بدء التفاعل مع البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # هنا نعرض تبويبات الفروع
    await branches(update, context)

def main():
    keep_alive()  # تشغيل السيرفر الخاص بالبوت

    app = Application.builder().token(TOKEN).build()

    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))

    # إضافة مستمع للرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_salary))

    # إضافة مستمع لردود الفروع (التفاعل مع الأزرار)
    app.add_handler(CallbackQueryHandler(button))

    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == "__main__":
    main()
