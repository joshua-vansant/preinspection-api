from app import app, db
from models.template import Template
from models.template_item import TemplateItem

def seed_default_template():
    with app.app_context():
        # Check if the default template already exists
        if Template.query.filter_by(is_default=True).first():
            print("Default template already exists. Skipping seeding.")
            return
        # Create a default template
        default_template = Template(
            name="Default Template",
            created_by=1,  # Assuming the admin user has ID 1
            is_default=True
        )
        db.session.add(default_template)
        db.session.commit()

        # Create default template items
        default_items = [
            TemplateItem(name="Brakes", question="Are the brakes functioning properly?", template_id=default_template.id),
            TemplateItem(name="Lights", question="Are the lights working?", template_id=default_template.id),
            TemplateItem(name="Tires", question="Are the tires in good condition?", template_id=default_template.id),
            TemplateItem(name="Mirrors", question="Are the mirrors adjusted properly?", template_id=default_template.id),
            TemplateItem(name="Horn", question="Is the horn working?", template_id=default_template.id)
        ]
        db.session.bulk_save_objects(default_items)
        db.session.commit()
        print("Default template and items seeded successfully.")

if __name__ == "__main__":
    seed_default_template()