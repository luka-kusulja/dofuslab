"""empty message

Revision ID: 381785d20acf
Revises: 2e417a5b9059
Create Date: 2020-11-11 21:03:54.739185

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from app.database.model_spell import ModelSpell

# revision identifiers, used by Alembic.
revision = "381785d20acf"
down_revision = "2e417a5b9059"
branch_labels = None
depends_on = None

game_version_enum = sa.Enum("DOFUS_2", "DOFUS_RETRO", "DOFUS_TOUCH", name="gameversion")
game_version_pg_enum = postgresql.ENUM(
    "DOFUS_2", "DOFUS_RETRO", "DOFUS_TOUCH", name="gameversion", create_type=False
)


def add_game_version_column(table_name):
    op.add_column(
        table_name, sa.Column("game_version", game_version_enum, nullable=True),
    )
    op.execute("UPDATE {} SET game_version = 'DOFUS_2'".format(table_name))
    op.alter_column(table_name, "game_version", nullable=False)
    op.create_index(
        op.f("ix_{}_game_version".format(table_name)),
        table_name,
        ["game_version"],
        unique=False,
    )


def drop_all_non_dofus_2(table_names):
    for table_name in table_names:
        op.execute("DELETE FROM {} WHERE game_version <> 'DOFUS_2'".format(table_name))


def upgrade():
    add_game_version_column("buff")
    add_game_version_column("class")
    add_game_version_column("custom_set")
    add_game_version_column("custom_set_tag")
    add_game_version_column("item")
    op.create_index(
        op.f("ix_item_slot_game_version"), "item_slot", ["game_version"], unique=False
    )
    add_game_version_column("item_type")
    add_game_version_column("set")
    op.add_column(
        "spell", sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    add_game_version_column("spell")
    op.alter_column(
        "spell", "spell_variant_pair_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.create_foreign_key(
        op.f("fk_spell_class_id_class"),
        "spell",
        "class",
        ["class_id"],
        ["uuid"],
        ondelete="CASCADE",
    )
    session = Session(bind=op.get_bind())
    for spell in session.query(ModelSpell).all():
        spell.class_id = spell.spell_variant_pair.class_id
    session.commit()


def downgrade():
    drop_all_non_dofus_2(
        [
            "spell",
            "set",
            "item_type",
            "item",
            "custom_set_tag",
            "custom_set",
            "class",
            "buff",
        ]
    )
    op.drop_constraint(op.f("fk_spell_class_id_class"), "spell", type_="foreignkey")
    op.drop_index(op.f("ix_spell_game_version"), table_name="spell")
    op.alter_column(
        "spell",
        "spell_variant_pair_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )
    op.drop_column("spell", "game_version")
    op.drop_column("spell", "class_id")
    op.drop_index(op.f("ix_set_game_version"), table_name="set")
    op.drop_column("set", "game_version")
    op.drop_index(op.f("ix_item_type_game_version"), table_name="item_type")
    op.drop_column("item_type", "game_version")
    op.drop_index(op.f("ix_item_slot_game_version"), table_name="item_slot")
    op.drop_index(op.f("ix_item_game_version"), table_name="item")
    op.drop_column("item", "game_version")
    op.drop_index(op.f("ix_custom_set_tag_game_version"), table_name="custom_set_tag")
    op.drop_column("custom_set_tag", "game_version")
    op.drop_index(op.f("ix_custom_set_game_version"), table_name="custom_set")
    op.drop_column("custom_set", "game_version")
    op.drop_index(op.f("ix_class_game_version"), table_name="class")
    op.drop_column("class", "game_version")
    op.drop_index(op.f("ix_buff_game_version"), table_name="buff")
    op.drop_column("buff", "game_version")
