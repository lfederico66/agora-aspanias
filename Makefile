.PHONY: help up down rebuild logs shell migrate makemigrations createsuperuser test datos-sinteticos clean

help:
	@echo "Comandos disponibles:"
	@echo "  make up                    Levanta el entorno Docker (web + postgres)"
	@echo "  make down                  Detiene el entorno"
	@echo "  make rebuild               Reconstruye imágenes y levanta el entorno"
	@echo "  make logs                  Muestra logs del servicio web"
	@echo "  make shell                 Abre shell de Django"
	@echo "  make migrate               Aplica migraciones"
	@echo "  make makemigrations        Genera nuevas migraciones"
	@echo "  make createsuperuser       Crea usuario administrador"
	@echo "  make test                  Ejecuta tests"
	@echo "  make datos-sinteticos      Carga datos sintéticos de prueba"
	@echo "  make clean                 Elimina volúmenes y datos locales"

up:
	docker compose -f infraestructura/docker-compose.yml up -d

down:
	docker compose -f infraestructura/docker-compose.yml down

rebuild:
	docker compose -f infraestructura/docker-compose.yml up -d --build

logs:
	docker compose -f infraestructura/docker-compose.yml logs -f web

shell:
	docker compose -f infraestructura/docker-compose.yml exec web python manage.py shell

migrate:
	docker compose -f infraestructura/docker-compose.yml exec web python manage.py migrate

makemigrations:
	docker compose -f infraestructura/docker-compose.yml exec web python manage.py makemigrations

createsuperuser:
	docker compose -f infraestructura/docker-compose.yml exec web python manage.py createsuperuser

test:
	docker compose -f infraestructura/docker-compose.yml exec web pytest

datos-sinteticos:
	docker compose -f infraestructura/docker-compose.yml exec web python manage.py cargar_datos_sinteticos

clean:
	docker compose -f infraestructura/docker-compose.yml down -v
