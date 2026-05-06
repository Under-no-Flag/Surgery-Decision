from app import app, db
from models import Config

def init_db():
    with app.app_context():
        db.create_all()

        # Check if configs exist
        if not Config.query.first():
            default_configs = [
                Config(key="base", value_float=5.3197),
                Config(key="position", value_float=-0.4604),
                Config(key="surgery_level", value_float=-0.6223),
                Config(key="surgery_method", value_float=-0.3634),
                Config(key="bmi", value_float=-0.0897),
                Config(key="hypothermia", value_float=1.0467),
                Config(key="albumin_abnormal", value_float=0.6037),
                Config(key="glucose_abnormal", value_float=0.6432),
                Config(key="surgery_time", value_float=0.0019),
                Config(key="suggestion_low", value_text="建议（1）保持受压部位皮肤清洁、干燥；（2）使用具有记忆海绵手术床垫，弹性和支撑度良好；（3）规范安置手术体位，保持肢体、躯干处于功能位，避免过度牵拉增加剪切力；（4）使用棉质/海绵/凝胶/流体等材质体位垫托起肢体；（5）采用综合保温措施，维持核心体温在正常范围内；（6）遵医嘱选择输注液体或血制品类别，维持循环稳定；（7）术中调整或变换手术体位时，受压部位增加棉质/海绵/凝胶/流体等体位垫进行减压预防。"),
                Config(key="suggestion_medium", value_text="建议（1）保持受压部位皮肤清洁、干燥；（2）使用具有记忆海绵手术床垫，弹性和支撑度良好；（3）规范安置手术体位，保持肢体、躯干处于功能位，避免过度牵拉增加剪切力；（4）使用棉质/海绵/凝胶/流体等材质体位垫托起肢体；（5）体位安置前在手术床上使用凝胶/流体等材质体位垫，受压部位皮肤应采用预防性敷料；（6）采用综合保温措施，维持核心体温在正常范围内；（7）遵医嘱选择输注液体或血制品类别，维持循环稳定；（8）术中调整或变换手术体位时，受压部位增加棉质/海绵/凝胶/流体等体位垫进行减压预防。"),
                Config(key="suggestion_high", value_text="建议（1）保持受压部位皮肤清洁、干燥；（2）使用具有记忆海绵手术床垫，弹性和支撑度良好；（3）规范安置手术体位，保持肢体、躯干处于功能位，避免过度牵拉增加剪切力；（4）使用棉质/海绵/凝胶/流体等材质体位垫托起肢体；（5）体位安置前在手术床上使用凝胶/流体等材质体位垫，受压部位皮肤应采用预防性敷料；（6）采用综合保温措施，维持核心体温在正常范围内；（7）遵医嘱选择输注液体或血制品类别，维持循环稳定；（8）术中调整或变换手术体位时，受压部位增加棉质/海绵/凝胶/流体等体位垫进行减压预防；（9）在手术允许情况下，术中针对受压部位进行手术体位微调整。")
            ]
            db.session.bulk_save_objects(default_configs)
            db.session.commit()
            print("Database initialized with default configurations.")
        else:
            print("Database already initialized.")

if __name__ == '__main__':
    init_db()
