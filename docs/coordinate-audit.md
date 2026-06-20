# Coordinate Audit

Audit date: 2026-06-20

Coordinate system: WGS84 latitude/longitude.

Current Overpass database snapshot checked: `2026-06-20T16:19:46Z`.

## Result

- Total graph nodes checked: `32`
- Total graph edges checked: `46`
- Duplicate node IDs: none
- Nodes outside DTU bounds: none
- Broken edge references: none
- Coordinate pairs closer than 30 meters: none
- Named OSM-backed coordinates with mismatch from current OSM: none

## High-Confidence Named OSM Matches

These nodes exactly match a current named OSM node, way center, or relation center.

| App node | App label | OSM label |
| --- | --- | --- |
| `dtu_entrance` | Main Gate Entry / Exit | DTU Entrance |
| `delhi_school_management` | Delhi School of Management | Delhi School of Management |
| `post_office` | DCE Post Office | DCE Post Office |
| `sbi` | State Bank of India (SBI) | State Bank of India |
| `parking` | DCE Parking | DCE Parking |
| `admin_block` | Administrative Building | Admin Block |
| `ambedkar_auditorium` | Dr. B. R. Ambedkar Auditorium | Dr BR Ambedkar Auditorium |
| `dtu_library` | Central Library | DTU Library |
| `nescafe` | Nescafe | Nescafe |
| `open_air_theatre` | Open Air Theater | Open Air Theatre |
| `science_block` | Academic Department Block 10 / Science Block | Science Block |
| `sps_classrooms` | Academic Department Block 11 / SPS Classrooms | SPS Classrooms |
| `mechanical_department` | Academic Department Block 9 / Mechanical Engineering | Department of Mechanical Engineering |
| `dtu_canteen` | Main Canteen of DTU Campus | DTU Canteen |
| `pragya_bhawan` | Pragyan Bhawan | Pragya Bhawan |
| `dtu_lake` | Pond | DTU Lake |
| `apj_hostel` | Dr. A.P.J. Abdul Kalam Hostel | APJ Hostel |
| `hjb_hostel` | HJB Hostel | HJB Hostel |
| `mini_park` | Mini Park | Mini Park |
| `raj_soin_hall` | Raj Soin Hall | Raj Soin Hall |
| `vvs_hostel` | VVS Hostel | VVS Hostel |
| `cvr_hostel` | CVR Hostel | CVR Hostel |
| `monkey_bridge` | Monkey Bridge | Monkey Bridge |
| `sports_complex` | Sports Complex | DTU Sports Complex |
| `gymnasium` | DTU Gymnasium | DTU Gymnasium |
| `badminton_court` | Indoor Badminton Court | Indoor Badminton Court |

## Official-Map Label With OSM Name Mismatch

| App node | App label | OSM label | Notes |
| --- | --- | --- | --- |
| `virangana_laxmi_bai_hostel` | Virangana Laxmi Bai Hostel | Sister Nivedita Hostel | Coordinate matches the OSM building footprint exactly. Label comes from DTU Annual Report 2023-24 official campus map item `25`. Treat this as an official-label override unless DTU/OSM confirms these are separate buildings. |

## Official-Map Matches Using Unnamed OSM Building Footprints

These coordinates match current OSM building footprints, but those footprints do not have names in OSM. The app labels come from DTU Annual Report 2023-24 page 2.

| App node | App label | Official map number | Coordinate source |
| --- | --- | --- | --- |
| `new_academic_block_17a` | Newly Constructed Academic Block 17A | `17A` | Unnamed OSM building footprint |
| `new_academic_block_17b` | Newly Constructed Academic Block 17B | `17B` | Unnamed OSM building footprint |
| `department_design` | Department of Design | `12` | Unnamed OSM building footprint |
| `computer_centre` | Computer Centre | `15` | Unnamed OSM building footprint |
| `academic_department_4_7` | Academic Department Block 4-7 | `4/5/6/7` | Unnamed OSM multipolygon footprint |

## Not Added As Separate Nodes

`Academic Block No. 6 / AB-6` appears in DTU official committee/minutes references as a project item, but I did not find a current named OSM feature or a confidently separable coordinate-backed footprint for it. The app currently represents official map item `4/5/6/7` as one route node: `academic_department_4_7`.

## Sources

- DTU Annual Report 2023-24, page 2 campus map: https://iqac.dtu.ac.in/ar/pdf/ar23-24_english.pdf
- DTU Campus Map page: https://dtu.ac.in/Web/About/campusmap.php
- OSM DTU campus way: https://www.openstreetmap.org/way/111212532
- Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
