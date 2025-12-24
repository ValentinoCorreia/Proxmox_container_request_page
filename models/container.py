from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String as AlchemyString, ForeignKey, Enum as AlchemyEnum

from models.connection import db

class ContainerRequestStatus(Enum):
    requested = 0
    approved = 1
    refused = 2

class ContainerTemplate(db.Model):
    __tablename__ = "container_template"

    name: Mapped[str] = mapped_column(primary_key=True)
    proxmox_os_template: Mapped[str] = mapped_column(nullable=False)
    
    

class Container(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id usato dall'applicativo
    name: Mapped[str] = mapped_column(AlchemyString(length=80))
    cpu_limit: Mapped[int] = mapped_column(default=0)
    ram: Mapped[int] = mapped_column(default=512)
    template_name: Mapped[str] = mapped_column(ForeignKey("container_template.name"))
    template: Mapped[ContainerTemplate] = relationship(foreign_keys=[template_name])
    initial_root_password: Mapped[str] = mapped_column(nullable=False)
    container_status = mapped_column(AlchemyEnum(ContainerRequestStatus)) # id usato da Proxmox
    lxc_proxmox_id: Mapped[int] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates="containers")
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))