# Laboratorio 07: balanceo de carga

Prácticas de balanceo local con Nginx y en AWS con un Application Load Balancer (ALB).

## Arquitectura

- **Local:** Nginx distribuye peticiones a tres servidores Python en los puertos 8081, 8082 y 8083.
- **AWS:** `alb-lab-web` distribuye HTTP a `web-server-1` (us-east-1a) y `web-server-2` (us-east-1b) mediante `tg-lab-web`.
- **Aplicación AWS:** inicio de sesión y operaciones CRUD de productos, servidos por las instancias EC2.

## Estado inicial recuperado

La VPC `vpc-045ce6eb3cb5da551`, las dos EC2, el grupo de destinos y el ALB ya existían. Las EC2 estaban detenidas; el ALB respondía HTTP 503. Se retomó el trabajo sin recrear esos recursos.

## Contenido

- `local/`: configuración, scripts y pruebas del balanceador local.
- `aws/`: scripts de arranque y pruebas de balanceo en AWS.
- `evidencias/`: capturas y resultados obtenidos durante las pruebas.
- `docs/`: informe, resultados y conclusiones.

## Costos

El ALB y las instancias EC2 pueden consumir créditos de AWS. Al terminar las demostraciones se deben revisar y apagar o eliminar los recursos que ya no se necesiten.
