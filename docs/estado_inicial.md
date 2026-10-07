# Estado recuperado el 7 de octubre de 2026

| Recurso | Estado al retomar |
|---|---|
| VPC | `vpc-lab-lb-vpc` (`10.0.0.0/16`) |
| EC2 1 | `web-server-1`, `t3.micro`, us-east-1a, detenida |
| EC2 2 | `web-server-2`, `t3.micro`, us-east-1b, detenida |
| Grupo de destinos | `tg-lab-web`, HTTP:80, ambas EC2 registradas |
| ALB | `alb-lab-web`, activo, dos zonas públicas |
| Prueba HTTP inicial | 503, debido a destinos detenidos |

El documento de avance previo solo contenía capturas de la creación de la VPC y las instancias. Las capturas antiguas no se usan como prueba del estado actual.
