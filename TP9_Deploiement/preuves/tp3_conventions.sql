-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: tp3_conventions
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.5

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `convention`
--

DROP TABLE IF EXISTS `convention`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `convention` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `etudiant_id` int unsigned NOT NULL,
  `entreprise_id` int unsigned NOT NULL,
  `encadreur_id` int unsigned DEFAULT NULL,
  `intitule` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `statut` enum('BROUILLON','SOUMISE','VALIDEE','REFUSEE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'BROUILLON',
  `motif_refus` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_depot` datetime DEFAULT NULL,
  `date_decision` datetime DEFAULT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_convention_id_encadreur` (`id`,`encadreur_id`),
  KEY `idx_convention_etudiant` (`etudiant_id`),
  KEY `idx_convention_entreprise` (`entreprise_id`),
  KEY `idx_convention_encadreur` (`encadreur_id`),
  KEY `idx_convention_statut` (`statut`),
  CONSTRAINT `fk_convention_encadreur` FOREIGN KEY (`encadreur_id`) REFERENCES `encadreur` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_convention_entreprise` FOREIGN KEY (`entreprise_id`) REFERENCES `entreprise` (`id`),
  CONSTRAINT `fk_convention_etudiant` FOREIGN KEY (`etudiant_id`) REFERENCES `etudiant` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_convention_decision` CHECK (((`statut` not in (_utf8mb4'VALIDEE',_utf8mb4'REFUSEE')) or (`date_decision` is not null))),
  CONSTRAINT `ck_convention_depot` CHECK (((`statut` = _utf8mb4'BROUILLON') or (`date_depot` is not null))),
  CONSTRAINT `ck_convention_motif` CHECK (((`statut` <> _utf8mb4'REFUSEE') or (`motif_refus` is not null))),
  CONSTRAINT `ck_convention_periode` CHECK ((`date_fin` > `date_debut`))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `convention`
--

LOCK TABLES `convention` WRITE;
/*!40000 ALTER TABLE `convention` DISABLE KEYS */;
INSERT INTO `convention` VALUES (1,1,1,NULL,'Application de suivi des tournées de collecte','BROUILLON',NULL,NULL,NULL,'2027-02-01','2027-05-31'),(2,2,2,NULL,'Tableau de bord des indicateurs territoriaux','SOUMISE',NULL,'2026-11-10 09:30:00',NULL,'2027-03-01','2027-06-30'),(3,3,1,1,'Refonte du portail documentaire','VALIDEE',NULL,'2026-10-15 10:00:00','2026-10-22 16:00:00','2027-01-11','2027-04-30'),(4,1,2,2,'Automatisation des rapports de collecte','VALIDEE',NULL,'2026-10-18 14:00:00','2026-10-25 11:30:00','2027-02-08','2027-05-28'),(5,2,1,NULL,'Maintenance du réseau de capteurs','REFUSEE','Période de stage incompatible avec le calendrier de la filière','2026-10-08 08:45:00','2026-10-12 15:10:00','2027-01-04','2027-03-29'),(6,3,2,NULL,'Entrepôt de données des conventions','VALIDEE',NULL,'2026-10-20 11:00:00','2026-10-28 09:00:00','2027-02-15','2027-06-15');
/*!40000 ALTER TABLE `convention` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disponibilite`
--

DROP TABLE IF EXISTS `disponibilite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disponibilite` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `encadreur_id` int unsigned NOT NULL,
  `date_debut` datetime NOT NULL,
  `date_fin` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_disponibilite_creneau` (`encadreur_id`,`date_debut`),
  KEY `idx_disponibilite_encadreur` (`encadreur_id`),
  CONSTRAINT `fk_disponibilite_encadreur` FOREIGN KEY (`encadreur_id`) REFERENCES `encadreur` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_disponibilite_ordre` CHECK ((`date_fin` > `date_debut`))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disponibilite`
--

LOCK TABLES `disponibilite` WRITE;
/*!40000 ALTER TABLE `disponibilite` DISABLE KEYS */;
INSERT INTO `disponibilite` VALUES (1,1,'2027-06-15 08:00:00','2027-06-15 12:00:00'),(2,1,'2027-06-16 08:00:00','2027-06-16 12:00:00'),(3,2,'2027-06-15 08:00:00','2027-06-15 12:00:00'),(4,2,'2027-06-17 14:00:00','2027-06-17 18:00:00');
/*!40000 ALTER TABLE `disponibilite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `encadreur`
--

DROP TABLE IF EXISTS `encadreur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `encadreur` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int unsigned NOT NULL,
  `grade` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `specialite` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_encadreur_utilisateur` (`utilisateur_id`),
  CONSTRAINT `fk_encadreur_utilisateur` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateur` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `encadreur`
--

LOCK TABLES `encadreur` WRITE;
/*!40000 ALTER TABLE `encadreur` DISABLE KEYS */;
INSERT INTO `encadreur` VALUES (1,4,'Maître de conférences','Bases de données'),(2,5,'Assistant','Génie logiciel');
/*!40000 ALTER TABLE `encadreur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entreprise`
--

DROP TABLE IF EXISTS `entreprise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entreprise` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nom` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ville` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_entreprise_nom_ville` (`nom`,`ville`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entreprise`
--

LOCK TABLES `entreprise` WRITE;
/*!40000 ALTER TABLE `entreprise` DISABLE KEYS */;
INSERT INTO `entreprise` VALUES (1,'Studio Kora','Porto-Novo','contact@studio-kora.test'),(2,'Données et Territoires','Cotonou','rh@donnees-territoires.test');
/*!40000 ALTER TABLE `entreprise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etudiant`
--

DROP TABLE IF EXISTS `etudiant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etudiant` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int unsigned NOT NULL,
  `numero_etudiant` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `filiere` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_etudiant_utilisateur` (`utilisateur_id`),
  UNIQUE KEY `uk_etudiant_numero` (`numero_etudiant`),
  CONSTRAINT `fk_etudiant_utilisateur` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateur` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etudiant`
--

LOCK TABLES `etudiant` WRITE;
/*!40000 ALTER TABLE `etudiant` DISABLE KEYS */;
INSERT INTO `etudiant` VALUES (1,1,'ETU-2026-014','SIL'),(2,2,'ETU-2026-027','SIL'),(3,3,'ETU-2026-039','SIL');
/*!40000 ALTER TABLE `etudiant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historique`
--

DROP TABLE IF EXISTS `historique`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historique` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `convention_id` int unsigned NOT NULL,
  `ancien_statut` enum('BROUILLON','SOUMISE','VALIDEE','REFUSEE') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nouveau_statut` enum('BROUILLON','SOUMISE','VALIDEE','REFUSEE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `auteur_id` int unsigned NOT NULL,
  `motif` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_evenement` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_historique_convention_date` (`convention_id`,`date_evenement`),
  KEY `idx_historique_auteur` (`auteur_id`),
  CONSTRAINT `fk_historique_auteur` FOREIGN KEY (`auteur_id`) REFERENCES `utilisateur` (`id`),
  CONSTRAINT `fk_historique_convention` FOREIGN KEY (`convention_id`) REFERENCES `convention` (`id`) ON DELETE CASCADE,
  CONSTRAINT `ck_historique_motif` CHECK (((`nouveau_statut` <> _utf8mb4'REFUSEE') or (`motif` is not null)))
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historique`
--

LOCK TABLES `historique` WRITE;
/*!40000 ALTER TABLE `historique` DISABLE KEYS */;
INSERT INTO `historique` VALUES (1,2,NULL,'SOUMISE',2,NULL,'2026-11-10 09:30:00'),(2,3,NULL,'SOUMISE',3,NULL,'2026-10-15 10:00:00'),(3,3,'SOUMISE','VALIDEE',6,NULL,'2026-10-22 16:00:00'),(4,4,NULL,'SOUMISE',1,NULL,'2026-10-18 14:00:00'),(5,4,'SOUMISE','VALIDEE',6,NULL,'2026-10-25 11:30:00'),(6,5,NULL,'SOUMISE',2,NULL,'2026-10-08 08:45:00'),(7,5,'SOUMISE','REFUSEE',6,'Période de stage incompatible avec le calendrier de la filière','2026-10-12 15:10:00'),(8,6,NULL,'SOUMISE',3,NULL,'2026-10-20 11:00:00'),(9,6,'SOUMISE','VALIDEE',6,NULL,'2026-10-28 09:00:00');
/*!40000 ALTER TABLE `historique` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salle`
--

DROP TABLE IF EXISTS `salle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salle` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `nom` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `capacite` smallint unsigned NOT NULL,
  `batiment` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_salle_nom` (`nom`),
  CONSTRAINT `ck_salle_capacite` CHECK ((`capacite` between 1 and 500))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salle`
--

LOCK TABLES `salle` WRITE;
/*!40000 ALTER TABLE `salle` DISABLE KEYS */;
INSERT INTO `salle` VALUES (1,'A-101',40,'Bâtiment A'),(2,'B-204',30,'Bâtiment B'),(3,'Amphi C',120,'Bâtiment C');
/*!40000 ALTER TABLE `salle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `soutenance`
--

DROP TABLE IF EXISTS `soutenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `soutenance` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `convention_id` int unsigned NOT NULL,
  `encadreur_id` int unsigned NOT NULL,
  `salle_id` int unsigned NOT NULL,
  `date_heure` datetime NOT NULL,
  `duree_min` smallint unsigned NOT NULL DEFAULT '45',
  `statut` enum('PLANIFIEE','REALISEE','ANNULEE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PLANIFIEE',
  `date_creation` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_soutenance_convention` (`convention_id`),
  UNIQUE KEY `uk_soutenance_salle_creneau` (`salle_id`,`date_heure`),
  UNIQUE KEY `uk_soutenance_encadreur_creneau` (`encadreur_id`,`date_heure`),
  KEY `idx_soutenance_convention_encadreur` (`convention_id`,`encadreur_id`),
  KEY `idx_soutenance_salle` (`salle_id`),
  CONSTRAINT `fk_soutenance_convention_encadreur` FOREIGN KEY (`convention_id`, `encadreur_id`) REFERENCES `convention` (`id`, `encadreur_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_soutenance_salle` FOREIGN KEY (`salle_id`) REFERENCES `salle` (`id`),
  CONSTRAINT `ck_soutenance_duree` CHECK ((`duree_min` between 20 and 240))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `soutenance`
--

LOCK TABLES `soutenance` WRITE;
/*!40000 ALTER TABLE `soutenance` DISABLE KEYS */;
INSERT INTO `soutenance` VALUES (1,3,1,1,'2027-06-15 09:00:00',45,'PLANIFIEE','2026-10-26 10:00:00'),(2,4,2,2,'2027-06-15 11:00:00',45,'PLANIFIEE','2026-10-30 09:30:00');
/*!40000 ALTER TABLE `soutenance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `utilisateur` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mot_de_passe_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('ETUDIANT','ENCADREUR','RESPONSABLE','ADMIN','DEVELOPPEUR') COLLATE utf8mb4_unicode_ci NOT NULL,
  `nom` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_utilisateur_email` (`email`),
  CONSTRAINT `ck_utilisateur_email` CHECK ((`email` like _utf8mb4'%_@_%._%'))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `utilisateur`
--

LOCK TABLES `utilisateur` WRITE;
/*!40000 ALTER TABLE `utilisateur` DISABLE KEYS */;
INSERT INTO `utilisateur` VALUES (1,'sena.houngbo@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ETUDIANT','HOUNGBO','Sènami',1),(2,'ibrahim.sanni@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ETUDIANT','SANNI','Ibrahim',1),(3,'grace.amegan@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ETUDIANT','AMEGAN','Grâce',1),(4,'sylvain.kiki@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ENCADREUR','KIKI','Sylvain',1),(5,'mireille.zinsou@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ENCADREUR','ZINSOU','Mireille',1),(6,'responsable.pedago@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','RESPONSABLE','ADJAHO','Pascal',1),(7,'admin.siege@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','ADMIN','da SILVA','Ruth',1),(8,'dev.equipe@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm','DEVELOPPEUR','TOSSA','Éric',1);
/*!40000 ALTER TABLE `utilisateur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_conventions_sans_encadreur`
--

DROP TABLE IF EXISTS `v_conventions_sans_encadreur`;
/*!50001 DROP VIEW IF EXISTS `v_conventions_sans_encadreur`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_conventions_sans_encadreur` AS SELECT 
 1 AS `convention_id`,
 1 AS `etudiant_nom`,
 1 AS `etudiant_prenom`,
 1 AS `numero_etudiant`,
 1 AS `date_decision`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_delai_publication`
--

DROP TABLE IF EXISTS `v_delai_publication`;
/*!50001 DROP VIEW IF EXISTS `v_delai_publication`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_delai_publication` AS SELECT 
 1 AS `convention_id`,
 1 AS `date_decision`,
 1 AS `date_publication`,
 1 AS `date_soutenance`,
 1 AS `delai_jours`,
 1 AS `cible_5j`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_planning_soutenance`
--

DROP TABLE IF EXISTS `v_planning_soutenance`;
/*!50001 DROP VIEW IF EXISTS `v_planning_soutenance`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_planning_soutenance` AS SELECT 
 1 AS `soutenance_id`,
 1 AS `date_heure`,
 1 AS `duree_min`,
 1 AS `statut_soutenance`,
 1 AS `salle`,
 1 AS `batiment`,
 1 AS `convention_id`,
 1 AS `intitule`,
 1 AS `numero_etudiant`,
 1 AS `etudiant`,
 1 AS `entreprise`,
 1 AS `encadreur`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_soutenances_conflits`
--

DROP TABLE IF EXISTS `v_soutenances_conflits`;
/*!50001 DROP VIEW IF EXISTS `v_soutenances_conflits`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_soutenances_conflits` AS SELECT 
 1 AS `soutenance_1`,
 1 AS `soutenance_2`,
 1 AS `type_conflit`,
 1 AS `salle_id`,
 1 AS `encadreur_id`,
 1 AS `debut_1`,
 1 AS `debut_2`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'tp3_conventions'
--

--
-- Final view structure for view `v_conventions_sans_encadreur`
--

/*!50001 DROP VIEW IF EXISTS `v_conventions_sans_encadreur`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_conventions_sans_encadreur` AS select `c`.`id` AS `convention_id`,`u`.`nom` AS `etudiant_nom`,`u`.`prenom` AS `etudiant_prenom`,`e`.`numero_etudiant` AS `numero_etudiant`,`c`.`date_decision` AS `date_decision` from ((`convention` `c` join `etudiant` `e` on((`e`.`id` = `c`.`etudiant_id`))) join `utilisateur` `u` on((`u`.`id` = `e`.`utilisateur_id`))) where ((`c`.`statut` = 'VALIDEE') and (`c`.`encadreur_id` is null)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_delai_publication`
--

/*!50001 DROP VIEW IF EXISTS `v_delai_publication`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_delai_publication` AS select `c`.`id` AS `convention_id`,`c`.`date_decision` AS `date_decision`,`s`.`date_creation` AS `date_publication`,`s`.`date_heure` AS `date_soutenance`,(to_days(`s`.`date_creation`) - to_days(`c`.`date_decision`)) AS `delai_jours`,(case when ((to_days(`s`.`date_creation`) - to_days(`c`.`date_decision`)) <= 5) then 'OUI' else 'NON' end) AS `cible_5j` from (`convention` `c` join `soutenance` `s` on((`s`.`convention_id` = `c`.`id`))) where (`c`.`statut` = 'VALIDEE') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_planning_soutenance`
--

/*!50001 DROP VIEW IF EXISTS `v_planning_soutenance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_planning_soutenance` AS select `s`.`id` AS `soutenance_id`,`s`.`date_heure` AS `date_heure`,`s`.`duree_min` AS `duree_min`,`s`.`statut` AS `statut_soutenance`,`sa`.`nom` AS `salle`,`sa`.`batiment` AS `batiment`,`c`.`id` AS `convention_id`,`c`.`intitule` AS `intitule`,`e`.`numero_etudiant` AS `numero_etudiant`,concat(`u`.`prenom`,' ',`u`.`nom`) AS `etudiant`,`ent`.`nom` AS `entreprise`,concat(`ue`.`prenom`,' ',`ue`.`nom`) AS `encadreur` from (((((((`soutenance` `s` join `convention` `c` on((`c`.`id` = `s`.`convention_id`))) join `etudiant` `e` on((`e`.`id` = `c`.`etudiant_id`))) join `utilisateur` `u` on((`u`.`id` = `e`.`utilisateur_id`))) join `entreprise` `ent` on((`ent`.`id` = `c`.`entreprise_id`))) join `salle` `sa` on((`sa`.`id` = `s`.`salle_id`))) join `encadreur` `enc` on((`enc`.`id` = `s`.`encadreur_id`))) join `utilisateur` `ue` on((`ue`.`id` = `enc`.`utilisateur_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_soutenances_conflits`
--

/*!50001 DROP VIEW IF EXISTS `v_soutenances_conflits`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_soutenances_conflits` AS select `a`.`id` AS `soutenance_1`,`b`.`id` AS `soutenance_2`,(case when ((`a`.`salle_id` = `b`.`salle_id`) and (`a`.`encadreur_id` = `b`.`encadreur_id`)) then 'SALLE+ENCADREUR' when (`a`.`salle_id` = `b`.`salle_id`) then 'SALLE' else 'ENCADREUR' end) AS `type_conflit`,`a`.`salle_id` AS `salle_id`,`a`.`encadreur_id` AS `encadreur_id`,`a`.`date_heure` AS `debut_1`,`b`.`date_heure` AS `debut_2` from (`soutenance` `a` join `soutenance` `b` on(((`a`.`id` < `b`.`id`) and (`a`.`statut` <> 'ANNULEE') and (`b`.`statut` <> 'ANNULEE') and ((`a`.`salle_id` = `b`.`salle_id`) or (`a`.`encadreur_id` = `b`.`encadreur_id`)) and (`a`.`date_heure` < (`b`.`date_heure` + interval `b`.`duree_min` minute)) and (`b`.`date_heure` < (`a`.`date_heure` + interval `a`.`duree_min` minute))))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-20  9:35:27
