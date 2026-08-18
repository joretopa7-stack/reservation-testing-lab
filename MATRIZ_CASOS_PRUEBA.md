# Matriz de casos de prueba — Reservation Testing Lab

| ID     | Regla  | Tipo       | Datos de entrada                                   | Resultado esperado                                  | Prueba automatizada |
|--------|--------|------------|-----------------------------------------------------|-------------------------------------------------------|----------------------|
| CP-01  | RN-01  | Positiva   | `"  Ana Torres  "`                                   | Devuelve `"Ana Torres"` (recortado)                    | `test_validate_customer_name_strips_external_whitespace` |
| CP-02  | RN-01  | Negativa   | `"Jo"`                                               | `InvalidCustomerNameError`                             | `test_validate_customer_name_rejects_names_shorter_than_three_chars` |
| CP-03  | RN-01  | Frontera   | `"  Ana  "` (3 caracteres tras recorte)              | Devuelve `"Ana"`                                       | `test_validate_customer_name_accepts_exactly_three_chars_after_trim` |
| CP-04  | RN-02  | Positiva   | `"asesoria"`, `"  SOPORTE  "`, `"Demostracion"`      | Devuelve el servicio normalizado en minúsculas          | `test_validate_service_normalizes_allowed_services` (parametrizada) |
| CP-05  | RN-02  | Negativa   | `"consultoria"`                                      | `InvalidServiceError`                                  | `test_validate_service_rejects_unknown_service` |
| CP-06  | RN-03  | Positiva   | `30`, `60`                                           | Devuelve la duración recibida                           | `test_validate_duration_accepts_allowed_values` (parametrizada) |
| CP-07  | RN-03  | Negativa   | `15`, `45`, `90`                                     | `InvalidDurationError`                                 | `test_validate_duration_rejects_disallowed_values` (parametrizada) |
| CP-08  | RN-04  | Negativa   | Fecha `2026-08-10` con `current_date=2026-08-17`     | `InvalidReservationDateError`                          | `test_validate_reservation_date_rejects_past_date` |
| CP-09  | RN-04  | Frontera   | Fecha == `current_date` (`2026-08-17`, lunes)        | Se acepta la fecha                                      | `test_validate_reservation_date_accepts_the_current_date_itself` |
| CP-10  | RN-05  | Positiva   | Fecha `2026-08-18` (martes, día hábil futuro)        | Se acepta la fecha                                      | `test_validate_reservation_date_accepts_future_weekday` |
| CP-11  | RN-05  | Negativa   | Sábado `2026-08-22`, domingo `2026-08-23`            | `InvalidReservationDateError`                          | `test_validate_reservation_date_rejects_weekend_dates` (parametrizada) |
| CP-12  | RN-06  | Frontera   | Hora `08:00` (apertura exacta), duración 30          | Se acepta la hora                                        | `test_validate_reservation_time_accepts_valid_slots[apertura-exacta]` |
| CP-13  | RN-06  | Negativa   | Hora `07:59`, duración 30                            | `InvalidReservationTimeError`                          | `test_validate_reservation_time_rejects_time_before_opening` |
| CP-14  | RN-07  | Frontera   | Hora `16:30` + 30 min = termina exactamente `17:00`  | Se acepta la hora                                        | `test_validate_reservation_time_accepts_valid_slots[ultimo-bloque-30-min]` |
| CP-15  | RN-07  | Negativa   | Hora `16:31` + 30 min (termina después de las 17:00) | `InvalidReservationTimeError`                          | `test_validate_reservation_time_rejects_slots_ending_after_closing[termina-un-minuto-tarde]` |
| CP-16  | RN-09  | Positiva   | Datos válidos de reserva                             | La reserva creada tiene `status == "confirmed"`         | `test_create_valid_reservation_has_confirmed_status` |
| CP-17  | RN-10  | Positiva   | `confirmation_code_generator` fijo (`"CONF-0001"`)   | `reservation.confirmation_code == "CONF-0001"`           | `test_create_valid_reservation_uses_injected_confirmation_code` |
| CP-18  | RN-01/RN-02 | Positiva | Nombre y servicio con espacios/mayúsculas          | Quedan normalizados en la reserva creada                | `test_create_normalizes_customer_name_and_service` |
| CP-19  | RN-08  | Negativa   | Segunda reserva con misma fecha/hora que una existente | `DuplicateReservationError`                          | `test_create_rejects_duplicate_reservation_for_same_date_and_time` |
| CP-20  | RN-08  | Negativa   | Igual que CP-19                                      | El repositorio conserva solo 1 reserva                  | `test_duplicate_reservation_attempt_does_not_add_a_second_record` |
| CP-21  | Transversal | Negativa | Datos con nombre inválido (`"Jo"`)               | No se guarda ninguna reserva en el repositorio           | `test_invalid_reservation_is_not_saved_in_repository` |
| CP-22  | RN-01 a RN-07 | Negativa (parametrizada) | 5 variantes: nombre corto, servicio inválido, duración inválida, fecha de fin de semana, hora antes de apertura | Se lanza la excepción específica de cada regla y no se persiste nada | `test_create_rejects_invalid_data_for_each_business_rule` |
| CP-23  | Transversal | Independencia | Repositorio recién inyectado por fixture       | `repository.list() == []` al iniciar la prueba            | `test_repository_starts_empty_for_every_test` |
| CP-24  | Transversal | Independencia | Se crea una reserva en una prueba              | Otra prueba, con repositorio nuevo, no ve esa reserva      | `test_creating_a_reservation_in_one_test_does_not_leak_into_another` |

**Total de casos ejecutables: 24** (mínimo exigido: 15).

## Resumen frente a los requisitos mínimos

| Requisito                                   | Mínimo | Alcanzado |
|----------------------------------------------|--------|-----------|
| Pruebas positivas                             | 5      | 9 (CP-01, 03, 04, 06, 09, 10, 12, 14, 16, 17, 18) |
| Pruebas negativas                             | 5      | 12 (CP-02, 05, 07, 08, 11, 13, 15, 19, 20, 21, 22) |
| Casos de frontera                             | 4      | 4 (CP-03, 09, 12, 14) |
| Casos parametrizados                          | 4      | 6 (`test_validate_service_normalizes_allowed_services`, `test_validate_duration_accepts_allowed_values`, `test_validate_duration_rejects_disallowed_values`, `test_validate_reservation_date_rejects_weekend_dates`, `test_validate_reservation_time_accepts_valid_slots`, `test_validate_reservation_time_rejects_slots_ending_after_closing`, `test_create_rejects_invalid_data_for_each_business_rule`) |
| Fixtures reutilizables                        | 4      | 5 (`current_date`, `valid_reservation_data`, `repository`, `confirmation_code_generator`, `reservation_service`) |
| Casos ejecutados totales                      | 15     | 39 pruebas físicas ejecutadas por pytest |
| Prueba de reserva duplicada                   | 1      | CP-19, CP-20 |
| Prueba de no persistencia ante error          | 1      | CP-21, CP-22 |
| Prueba de independencia del repositorio       | 1      | CP-23, CP-24 |
