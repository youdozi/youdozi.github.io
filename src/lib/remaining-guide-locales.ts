// Full translations of the English guide copy; curated keys stay in the source definitions.
export const remainingGuideLocales = {
  "zh-CN": {
    "jdk": {
      "label": "JDK 功能指南",
      "title": "JDK 指南：正式 API、预览历史与二进制检查",
      "eyebrow": "JDK",
      "description": "区分 JDK 21 的正式功能与预览功能，了解 String Templates 的历史，并在各篇文章记录的范围内检查 JDK 二进制元数据。",
      "intro": "区分语言或 API 的状态与实际安装的运行时。这些文章包含历史发布事件与预览资料；请遵循记录的版本，不要根据旧版发布说明推断当前支持情况。",
      "groups": {
        "features": {
          "title": "区分功能状态",
          "description": "从正式 API 与预览功能的适用范围开始。"
        },
        "preview": {
          "title": "阅读预览历史",
          "description": "了解 String Templates，以及文章中展示的标准格式化替代方案。"
        },
        "binaries": {
          "title": "检查运行时二进制文件",
          "description": "将历史上的 Temurin 发布延迟与平台及二进制元数据检查分开。"
        }
      }
    },
    "automation": {
      "label": "发布流程指南",
      "title": "发布流程指南：草稿审核、CI 与部署",
      "eyebrow": "审核后发布",
      "description": "了解从自动发布转向草稿 PR 审核的过程，并区分检查通过与获准的生产部署。",
      "intro": "先将候选内容准备为草稿，检查变更，再在批准后发布。这些文章追踪本仓库的流程与可执行测试样例；PR 检查通过本身不能证明生产部署完成或内容准确。",
      "groups": {
        "drafts": {
          "title": "准备可审核的草稿",
          "description": "从候选内容准备开始，了解发布前的审核边界。"
        },
        "deployment": {
          "title": "区分检查与部署",
          "description": "追踪可复用检查、事件条件与生产部署证据。"
        }
      }
    },
    "jenkins": {
      "label": "Jenkins 恢复指南",
      "title": "Jenkins Docker 指南：启动、持久化与备份恢复",
      "eyebrow": "Docker 中的 Jenkins",
      "description": "启动一次性 Jenkins 控制器，验证重新创建容器后的状态，再将已停止控制器的主目录恢复到新的 Docker 卷。",
      "intro": "先检查启动与持久存储，再尝试备份恢复。示例使用一次性控制器，对比 HTTP 就绪状态、标记与初始密码。它们不能证明生产工作负载恢复或凭据解密成功。",
      "groups": {
        "persistence": {
          "title": "验证启动与持久化",
          "description": "检查就绪状态，以及重新创建容器后保留的状态。"
        },
        "restore": {
          "title": "恢复到新卷",
          "description": "停止源控制器，将 master.key 与归档分开，再验证恢复后的状态。"
        }
      }
    },
    "jekyll": {
      "label": "Ruby 与 Jekyll 环境指南",
      "title": "Ruby 与 Jekyll 指南：Bundle 环境与原生编译器检查",
      "eyebrow": "旧版 Ruby 诊断",
      "description": "确认所选 Ruby 与 Bundler 环境，渲染隔离的旧版 Jekyll 测试样例，并将原生编译器检查与 gem 安装区分开。",
      "intro": "先确认 Ruby 可执行文件与声明的 bundle，再隔离编译器故障。这些示例复现不再受支持的 Ruby 3.2.2 环境。两页渲染或独立 C++ 探测不能验证完整站点或原生 gem 重建。",
      "groups": {
        "bundle": {
          "title": "检查运行时与 bundle",
          "description": "确认所选可执行文件，并用声明的旧版 bundle 渲染两页。"
        },
        "compiler": {
          "title": "隔离编译器故障",
          "description": "区分 Ruby 构建配置与临时 C++ 程序使用的编译器及 SDK 输入。"
        }
      }
    }
  },
  "ja": {
    "jdk": {
      "label": "JDK 機能ガイド",
      "title": "JDK ガイド：正式 API・プレビューの経緯・バイナリーの確認",
      "eyebrow": "JDK",
      "description": "JDK 21 の正式機能とプレビュー機能を区別し、String Templates の経緯を理解して、各記事に記録された範囲で JDK バイナリーのメタデータを調べます。",
      "intro": "言語・API の状態と実際にインストールするランタイムを区別します。過去のリリースとプレビュー資料を含むため、記録されたバージョンに従い、古いリリースノートから現在のサポート状況を推測しないでください。",
      "groups": {
        "features": {
          "title": "機能の状態を区別する",
          "description": "正式 API とプレビュー機能の適用範囲から確認します。"
        },
        "preview": {
          "title": "プレビューの経緯を読む",
          "description": "String Templates と、記事で示す標準的な書式設定の代替手段を理解します。"
        },
        "binaries": {
          "title": "ランタイムのバイナリーを調べる",
          "description": "過去の Temurin リリース遅延と、プラットフォーム・バイナリーメタデータの確認を区別します。"
        }
      }
    },
    "automation": {
      "label": "公開フローガイド",
      "title": "公開フローガイド：草稿レビュー・CI・デプロイ",
      "eyebrow": "レビュー後の公開",
      "description": "自動公開から草稿 PR のレビューへの移行をたどり、検査の成功と承認済みの本番デプロイを区別します。",
      "intro": "候補を草稿として準備し、変更を確認して承認後に公開します。記事ではこのリポジトリのフローと実行可能なテスト用データをたどります。PR 検査の成功だけでは、本番デプロイや内容の正確性は証明されません。",
      "groups": {
        "drafts": {
          "title": "レビュー可能な草稿を準備する",
          "description": "候補の準備から公開前のレビュー境界まで確認します。"
        },
        "deployment": {
          "title": "検査とデプロイを区別する",
          "description": "再利用可能な検査、イベント条件、本番デプロイの証拠をたどります。"
        }
      }
    },
    "jenkins": {
      "label": "Jenkins 復旧ガイド",
      "title": "Jenkins Docker ガイド：起動・永続化・バックアップ復元",
      "eyebrow": "Docker 上の Jenkins",
      "description": "使い捨ての Jenkins コントローラーを起動し、コンテナー再作成を検証した後、停止したコントローラーのホームを新しい Docker ボリュームに復元します。",
      "intro": "バックアップの復元を試みる前に、起動と永続ストレージを確認します。例では使い捨てのコントローラーで HTTP の準備状態・マーカー・初期パスワードを比較します。本番ワークロードの復旧や認証情報の復号を証明するものではありません。",
      "groups": {
        "persistence": {
          "title": "起動と永続性を検証する",
          "description": "準備状態と、コンテナー再作成後に保持された状態を確認します。"
        },
        "restore": {
          "title": "新しいボリュームに復元する",
          "description": "元のコントローラーを停止し、master.key をアーカイブと分離して、復元状態を検証します。"
        }
      }
    },
    "jekyll": {
      "label": "Ruby・Jekyll 環境ガイド",
      "title": "Ruby・Jekyll ガイド：Bundle 環境とネイティブコンパイラーの確認",
      "eyebrow": "旧 Ruby 環境の診断",
      "description": "選択された Ruby と Bundler の環境を特定し、隔離した旧 Jekyll のテスト用データをレンダリングして、ネイティブコンパイラーの確認と gem インストールを区別します。",
      "intro": "Ruby 実行ファイルと宣言された bundle から確認し、コンパイラーの失敗を切り分けます。例はサポート終了済みの Ruby 3.2.2 環境を再現します。2 ページのレンダリングや独立した C++ の検査では、サイト全体やネイティブ gem の再ビルドは検証できません。",
      "groups": {
        "bundle": {
          "title": "ランタイムと bundle を確認する",
          "description": "選択された実行ファイルを特定し、宣言された旧 bundle で 2 ページをレンダリングします。"
        },
        "compiler": {
          "title": "コンパイラーの失敗を切り分ける",
          "description": "Ruby のビルド設定と、一時 C++ プログラムで使うコンパイラー・SDK の入力を区別します。"
        }
      }
    }
  },
  "de": {
    "jdk": {
      "label": "Anleitungen zu JDK-Funktionen",
      "title": "JDK: Finale APIs, Preview-Historie und Binärprüfungen",
      "eyebrow": "JDK",
      "description": "Finale und Preview-Funktionen von JDK 21 unterscheiden, die Geschichte von String Templates verstehen und JDK-Binärmetadaten im dokumentierten Umfang des jeweiligen Artikels prüfen.",
      "intro": "Trennen Sie den Status von Sprache und APIs von der tatsächlich installierten Laufzeit. Die Artikel enthalten historische Veröffentlichungen und Preview-Material; beachten Sie die angegebenen Versionen und leiten Sie aus alten Release Notes keinen aktuellen Supportstatus ab.",
      "groups": {
        "features": {
          "title": "Funktionsstatus unterscheiden",
          "description": "Mit finalen APIs und den Grenzen von Preview-Funktionen beginnen."
        },
        "preview": {
          "title": "Die Preview-Historie lesen",
          "description": "String Templates und die im Artikel gezeigte Alternative mit Standardformatierung verstehen."
        },
        "binaries": {
          "title": "Laufzeit-Binärdateien prüfen",
          "description": "Die historische Temurin-Verzögerung von Prüfungen der Plattform und Binärmetadaten trennen."
        }
      }
    },
    "automation": {
      "label": "Anleitungen zum Veröffentlichungsablauf",
      "title": "Veröffentlichungsablauf: Entwurfsprüfung, CI und Deployment",
      "eyebrow": "Veröffentlichung nach Prüfung",
      "description": "Den Übergang von automatischer Veröffentlichung zur Prüfung von Entwurfs-PRs nachvollziehen und erfolgreiche Prüfungen von einem genehmigten Produktionsdeployment unterscheiden.",
      "intro": "Bereiten Sie einen Kandidaten als Entwurf vor, prüfen Sie die Änderungen und veröffentlichen Sie nach Freigabe. Die Artikel behandeln den Workflow dieses Repositorys und ausführbare Test-Fixtures; ein erfolgreicher PR-Check allein belegt weder ein Produktionsdeployment noch die Richtigkeit des Inhalts.",
      "groups": {
        "drafts": {
          "title": "Einen prüfbaren Entwurf vorbereiten",
          "description": "Die Vorbereitung eines Kandidaten und die Prüfgrenze vor der Veröffentlichung nachvollziehen."
        },
        "deployment": {
          "title": "Prüfungen und Deployment trennen",
          "description": "Wiederverwendbare Prüfungen, Ereignisbedingungen und Belege für das Produktionsdeployment nachvollziehen."
        }
      }
    },
    "jenkins": {
      "label": "Anleitungen zur Jenkins-Wiederherstellung",
      "title": "Jenkins mit Docker: Start, Persistenz und Backup-Wiederherstellung",
      "eyebrow": "Jenkins in Docker",
      "description": "Einen temporären Jenkins-Controller starten, die Neuerstellung des Containers prüfen und dann das Home-Verzeichnis eines gestoppten Controllers in ein neues Docker-Volume wiederherstellen.",
      "intro": "Beginnen Sie mit Start und persistentem Speicher, bevor Sie ein Backup wiederherstellen. Die Beispiele verwenden temporäre Controller und vergleichen HTTP-Bereitschaft, eine Markierungsdatei und das initiale Passwort. Sie belegen weder die Wiederherstellung produktiver Workloads noch die Entschlüsselung von Zugangsdaten.",
      "groups": {
        "persistence": {
          "title": "Start und Persistenz prüfen",
          "description": "Bereitschaft und erhaltenen Zustand nach der Neuerstellung eines Containers prüfen."
        },
        "restore": {
          "title": "In ein neues Volume wiederherstellen",
          "description": "Den Quellcontroller stoppen, master.key vom Archiv trennen und den wiederhergestellten Zustand prüfen."
        }
      }
    },
    "jekyll": {
      "label": "Anleitungen zu Ruby- und Jekyll-Umgebungen",
      "title": "Ruby und Jekyll: Bundle-Kontext und native Compilerprüfungen",
      "eyebrow": "Diagnose älterer Ruby-Umgebungen",
      "description": "Die gewählte Ruby- und Bundler-Umgebung identifizieren, eine isolierte ältere Jekyll-Testumgebung rendern und native Compilerprüfungen von der Gem-Installation trennen.",
      "intro": "Beginnen Sie mit der Ruby-Programmdatei und dem deklarierten Bundle, bevor Sie Compilerfehler isolieren. Die Beispiele reproduzieren eine nicht mehr unterstützte Ruby-3.2.2-Umgebung. Ein Renderlauf mit zwei Seiten oder ein eigenständiger C++-Test prüft weder eine vollständige Website noch den Neubau eines nativen Gems.",
      "groups": {
        "bundle": {
          "title": "Laufzeit und Bundle prüfen",
          "description": "Die gewählte Programmdatei bestimmen und zwei Seiten mit dem deklarierten älteren Bundle rendern."
        },
        "compiler": {
          "title": "Compilerfehler isolieren",
          "description": "Ruby-Build-Konfiguration von den Compiler- und SDK-Eingaben eines temporären C++-Programms trennen."
        }
      }
    }
  },
  "fr": {
    "jdk": {
      "label": "Guides des fonctionnalités du JDK",
      "title": "JDK : API définitives, historique des previews et binaires",
      "eyebrow": "JDK",
      "description": "Distinguer les fonctionnalités définitives et en preview du JDK 21, comprendre l’historique des String Templates et examiner les métadonnées des binaires dans le périmètre consigné par chaque article.",
      "intro": "Distinguez le statut du langage et des API de l’environnement d’exécution réellement installé. Ces articles comprennent des événements de publication historiques et des fonctionnalités en preview ; respectez les versions indiquées et ne déduisez pas le support actuel d’une ancienne note de version.",
      "groups": {
        "features": {
          "title": "Distinguer le statut des fonctionnalités",
          "description": "Commencer par les API définitives et les limites des fonctionnalités en preview."
        },
        "preview": {
          "title": "Lire l’historique des previews",
          "description": "Comprendre les String Templates et l’alternative de formatage standard présentée dans l’article."
        },
        "binaries": {
          "title": "Examiner les binaires d’exécution",
          "description": "Séparer le retard historique de Temurin des contrôles de plateforme et de métadonnées des binaires."
        }
      }
    },
    "automation": {
      "label": "Guides du processus de publication",
      "title": "Publication : revue des brouillons, CI et déploiement",
      "eyebrow": "Publication après revue",
      "description": "Suivre le passage de la publication automatique à la revue des PR de brouillon, puis distinguer les contrôles réussis d’un déploiement en production autorisé.",
      "intro": "Préparez une proposition en brouillon, examinez les modifications et publiez après approbation. Les articles retracent le workflow de ce dépôt et ses jeux de test exécutables ; la réussite d’un contrôle de PR ne prouve à elle seule ni le déploiement en production ni l’exactitude du contenu.",
      "groups": {
        "drafts": {
          "title": "Préparer un brouillon à examiner",
          "description": "Suivre la préparation d’une proposition et la limite de revue avant publication."
        },
        "deployment": {
          "title": "Séparer contrôles et déploiement",
          "description": "Suivre les contrôles réutilisables, les conditions d’événement et les preuves de déploiement en production."
        }
      }
    },
    "jenkins": {
      "label": "Guides de restauration Jenkins",
      "title": "Jenkins avec Docker : démarrage, persistance et restauration",
      "eyebrow": "Jenkins dans Docker",
      "description": "Démarrer un contrôleur Jenkins jetable, vérifier la recréation du conteneur, puis restaurer le répertoire personnel d’un contrôleur arrêté dans un nouveau volume Docker.",
      "intro": "Commencez par le démarrage et le stockage persistant avant de tenter une restauration. Les exemples utilisent des contrôleurs jetables et comparent la disponibilité HTTP, un marqueur et le mot de passe initial. Ils ne prouvent ni la reprise des charges de production ni le déchiffrement des identifiants.",
      "groups": {
        "persistence": {
          "title": "Vérifier démarrage et persistance",
          "description": "Contrôler la disponibilité et l’état conservé après recréation d’un conteneur."
        },
        "restore": {
          "title": "Restaurer dans un nouveau volume",
          "description": "Arrêter le contrôleur source, séparer master.key de l’archive et vérifier l’état restauré."
        }
      }
    },
    "jekyll": {
      "label": "Guides des environnements Ruby et Jekyll",
      "title": "Ruby et Jekyll : contexte du bundle et compilateur natif",
      "eyebrow": "Diagnostic des anciens environnements Ruby",
      "description": "Identifier le contexte Ruby et Bundler sélectionné, rendre un jeu de test Jekyll ancien et isolé, puis distinguer les contrôles du compilateur natif de l’installation de gems.",
      "intro": "Commencez par l’exécutable Ruby et le bundle déclaré, puis isolez les échecs du compilateur. Les exemples reproduisent un environnement Ruby 3.2.2 qui n’est plus pris en charge. Un rendu de deux pages ou un test C++ autonome ne vérifie ni un site complet ni la reconstruction d’une gem native.",
      "groups": {
        "bundle": {
          "title": "Vérifier l’environnement et le bundle",
          "description": "Identifier l’exécutable sélectionné et rendre deux pages avec le bundle ancien déclaré."
        },
        "compiler": {
          "title": "Isoler les échecs du compilateur",
          "description": "Distinguer la configuration de compilation Ruby des paramètres du compilateur et du SDK utilisés par un programme C++ temporaire."
        }
      }
    }
  },
  "ru": {
    "jdk": {
      "label": "Руководства по возможностям JDK",
      "title": "JDK: окончательные API, история preview и проверка бинарных файлов",
      "eyebrow": "JDK",
      "description": "Различайте окончательные и предварительные возможности JDK 21, изучите историю String Templates и проверяйте метаданные бинарных файлов JDK в пределах, указанных в каждой статье.",
      "intro": "Отделяйте статус языка и API от фактически устанавливаемой среды выполнения. Статьи включают исторические выпуски и материалы о preview: используйте указанные версии и не определяйте текущую поддержку по старым примечаниям к выпуску.",
      "groups": {
        "features": {
          "title": "Различать статус возможностей",
          "description": "Начните с окончательных API и границ применения предварительных возможностей."
        },
        "preview": {
          "title": "Изучить историю preview",
          "description": "Разберитесь со String Templates и показанной в статье стандартной альтернативой форматирования."
        },
        "binaries": {
          "title": "Проверить бинарные файлы среды",
          "description": "Отделяйте историческую задержку Temurin от проверок платформы и метаданных бинарных файлов."
        }
      }
    },
    "automation": {
      "label": "Руководства по процессу публикации",
      "title": "Процесс публикации: проверка черновиков, CI и развёртывание",
      "eyebrow": "Публикация после проверки",
      "description": "Проследите переход от автоматической публикации к проверке черновых PR и отличайте успешные проверки от разрешённого развёртывания в рабочей среде.",
      "intro": "Подготовьте материал как черновик, изучите изменения и публикуйте после одобрения. Статьи описывают процесс этого репозитория и исполняемые тестовые примеры; успешная проверка PR сама по себе не доказывает развёртывание в рабочей среде или точность содержания.",
      "groups": {
        "drafts": {
          "title": "Подготовить черновик для проверки",
          "description": "Проследите подготовку материала и границу проверки перед публикацией."
        },
        "deployment": {
          "title": "Разделить проверки и развёртывание",
          "description": "Проследите повторно используемые проверки, условия событий и подтверждения развёртывания в рабочей среде."
        }
      }
    },
    "jenkins": {
      "label": "Руководства по восстановлению Jenkins",
      "title": "Jenkins в Docker: запуск, сохранение состояния и восстановление",
      "eyebrow": "Jenkins в Docker",
      "description": "Запустите одноразовый контроллер Jenkins, проверьте пересоздание контейнера, затем восстановите домашний каталог остановленного контроллера в новый том Docker.",
      "intro": "Начните с запуска и постоянного хранилища, прежде чем переходить к восстановлению резервной копии. Примеры используют одноразовые контроллеры и сравнивают готовность HTTP, маркер и начальный пароль. Они не доказывают восстановление рабочих нагрузок или расшифровку учётных данных.",
      "groups": {
        "persistence": {
          "title": "Проверить запуск и сохранение состояния",
          "description": "Проверьте готовность и сохранённое состояние после пересоздания контейнера."
        },
        "restore": {
          "title": "Восстановить в новый том",
          "description": "Остановите исходный контроллер, отделите master.key от архива и проверьте восстановленное состояние."
        }
      }
    },
    "jekyll": {
      "label": "Руководства по средам Ruby и Jekyll",
      "title": "Ruby и Jekyll: контекст bundle и проверка нативного компилятора",
      "eyebrow": "Диагностика старых сред Ruby",
      "description": "Определите выбранную среду Ruby и Bundler, отрендерите изолированный тестовый пример старого Jekyll и отделите проверки нативного компилятора от установки gem.",
      "intro": "Начните с исполняемого файла Ruby и объявленного bundle, затем изолируйте сбои компилятора. Примеры воспроизводят неподдерживаемую среду Ruby 3.2.2. Рендеринг двух страниц или отдельная проверка C++ не проверяют весь сайт или пересборку нативного gem.",
      "groups": {
        "bundle": {
          "title": "Проверить среду выполнения и bundle",
          "description": "Определите выбранный исполняемый файл и отрендерите две страницы с объявленным старым bundle."
        },
        "compiler": {
          "title": "Изолировать сбои компилятора",
          "description": "Отделите конфигурацию сборки Ruby от входных параметров компилятора и SDK, используемых временной программой C++."
        }
      }
    }
  },
  "es": {
    "jdk": {
      "label": "Guías de funciones del JDK",
      "title": "JDK: API definitivas, historial de previews y binarios",
      "eyebrow": "JDK",
      "description": "Distingue las funciones definitivas y en preview del JDK 21, conoce el historial de String Templates e inspecciona los metadatos de los binarios dentro del alcance registrado en cada artículo.",
      "intro": "Separa el estado del lenguaje y las API del entorno de ejecución que realmente instalas. Estos artículos incluyen publicaciones históricas y material de preview; respeta las versiones indicadas y no deduzcas el soporte actual de una nota de versión antigua.",
      "groups": {
        "features": {
          "title": "Distinguir el estado de las funciones",
          "description": "Empieza por las API definitivas y los límites de las funciones en preview."
        },
        "preview": {
          "title": "Leer el historial de previews",
          "description": "Comprende String Templates y la alternativa de formato estándar mostrada en el artículo."
        },
        "binaries": {
          "title": "Inspeccionar binarios de ejecución",
          "description": "Separa el retraso histórico de Temurin de las comprobaciones de plataforma y metadatos de binarios."
        }
      }
    },
    "automation": {
      "label": "Guías del proceso de publicación",
      "title": "Publicación: revisión de borradores, CI y despliegue",
      "eyebrow": "Publicación tras revisión",
      "description": "Sigue el paso de la publicación automática a la revisión de PR de borradores y distingue los controles superados de un despliegue en producción autorizado.",
      "intro": "Prepara una propuesta como borrador, revisa los cambios y publica tras la aprobación. Estos artículos recorren el flujo de este repositorio y sus ejemplos de prueba ejecutables; superar los controles de una PR por sí solo no demuestra un despliegue en producción ni la exactitud del contenido.",
      "groups": {
        "drafts": {
          "title": "Preparar un borrador revisable",
          "description": "Sigue la preparación de una propuesta y el límite de revisión previo a la publicación."
        },
        "deployment": {
          "title": "Separar controles y despliegue",
          "description": "Sigue los controles reutilizables, las condiciones de los eventos y las pruebas del despliegue en producción."
        }
      }
    },
    "jenkins": {
      "label": "Guías de recuperación de Jenkins",
      "title": "Jenkins con Docker: inicio, persistencia y restauración",
      "eyebrow": "Jenkins en Docker",
      "description": "Inicia un controlador Jenkins desechable, verifica la recreación del contenedor y restaura el directorio de un controlador detenido en un nuevo volumen Docker.",
      "intro": "Empieza por el inicio y el almacenamiento persistente antes de intentar una restauración. Los ejemplos usan controladores desechables y comparan la disponibilidad HTTP, un marcador y la contraseña inicial. No demuestran la recuperación de cargas de producción ni el descifrado de credenciales.",
      "groups": {
        "persistence": {
          "title": "Verificar inicio y persistencia",
          "description": "Comprueba la disponibilidad y el estado conservado tras recrear un contenedor."
        },
        "restore": {
          "title": "Restaurar en un volumen nuevo",
          "description": "Detén el controlador de origen, separa master.key del archivo de copia y verifica el estado restaurado."
        }
      }
    },
    "jekyll": {
      "label": "Guías de entornos Ruby y Jekyll",
      "title": "Ruby y Jekyll: contexto del bundle y compilador nativo",
      "eyebrow": "Diagnóstico de entornos Ruby antiguos",
      "description": "Identifica el contexto seleccionado de Ruby y Bundler, renderiza un ejemplo de prueba aislado de Jekyll antiguo y separa las comprobaciones del compilador nativo de la instalación de gems.",
      "intro": "Empieza por el ejecutable Ruby y el bundle declarado; después aísla los fallos del compilador. Los ejemplos reproducen un entorno Ruby 3.2.2 sin soporte. Renderizar dos páginas o ejecutar una prueba C++ independiente no verifica un sitio completo ni la recompilación de una gem nativa.",
      "groups": {
        "bundle": {
          "title": "Comprobar el entorno y el bundle",
          "description": "Identifica el ejecutable seleccionado y renderiza dos páginas con el bundle antiguo declarado."
        },
        "compiler": {
          "title": "Aislar fallos del compilador",
          "description": "Separa la configuración de compilación de Ruby de los parámetros del compilador y del SDK usados por un programa C++ temporal."
        }
      }
    }
  }
};
export const remainingGuideLocalesUpdatedAt = new Date("2026-10-30T01:48:54.471595+00:00");
