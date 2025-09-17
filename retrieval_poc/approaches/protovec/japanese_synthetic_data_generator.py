"""
Japanese synthetic data generator for prototype network training.
Creates training examples from Japanese rule descriptions since eval_ja.csv
doesn't have JSON examples like eval_en.csv.
"""

import pandas as pd
import json
import random
from typing import List, Dict, Any
import re
from tqdm import tqdm


class JapaneseSyntheticDataGenerator:
    """Generates synthetic training data from Japanese rule descriptions."""
    
    def __init__(self, csv_path: str):
        """Initialize with path to eval_ja.csv."""
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
        # Japanese expense type patterns
        self.expense_patterns = {
            'RULE_001': [
                "東京から新宿まで電車で500円",
                "大阪から京都までバスで800円", 
                "近隣の電車利用で300円",
                "短距離バス移動で200円"
            ],
            'RULE_002': [
                "東京から大阪まで新幹線で15000円",
                "羽田から福岡まで飛行機で25000円",
                "ホテル宿泊費20000円",
                "新幹線とホテルセットで35000円"
            ],
            'RULE_003': [
                "ソウルから釜山まで地下鉄で3000円",
                "ロンドンからパリまでバスで20ユーロ",
                "海外の近隣電車で500円",
                "海外出張の短距離移動で1000円"
            ],
            'RULE_004': [
                "日本からアメリカまで飛行機で80000円",
                "海外出張の新幹線チケットで50000円",
                "海外ホテル宿泊で60000円",
                "国際線飛行機とホテルで120000円"
            ],
            'RULE_005': [
                "深夜作業のためタクシーで3000円",
                "緊急で病院までタクシーで4500円",
                "タクシー利用理由：遅刻",
                "緊急時のタクシー代で2500円"
            ],
            'RULE_006': [
                "海外出張のタクシー代で5000円",
                "海外での緊急タクシー利用で3000円",
                "海外タクシー理由：会議",
                "海外でのタクシー移動で4000円"
            ],
            'RULE_007': [
                "接待のタクシー代で3000円",
                "お客様送迎のタクシーで4500円",
                "接待後のタクシー代で2000円",
                "お客様との食事後のタクシーで3500円"
            ],
            'RULE_008': [
                "国内出張の日当2000円",
                "一泊出張の日当4000円",
                "出張日当：2泊3日で4000円",
                "国内出張日当で2000円"
            ],
            'RULE_009': [
                "海外出張の日当で2000円",
                "海外一泊出張の日当で4000円",
                "海外出張日当：3泊4日で6000円",
                "海外出張の日当で2000円"
            ],
            'RULE_010': [
                "宿泊税で500円",
                "入湯税で300円",
                "宿泊税・入湯税で800円",
                "ホテル宿泊税で600円"
            ],
            'RULE_011': [
                "東名高速道路ETCで2500円",
                "中央道ETCで1800円",
                "高速道路ETC利用で3000円",
                "ETCカードで高速代2000円"
            ],
            'RULE_012': [
                "会議費で50000円",
                "セミナー費用で30000円",
                "会議・セミナー費用で40000円",
                "会議開催費用で60000円"
            ],
            'RULE_013': [
                "会議費（8%）で5000円",
                "セミナー費用（8%）で3000円",
                "会議・セミナー費用（8%）で4000円",
                "会議開催費用（8%）で6000円"
            ],
            'RULE_014': [
                "外部との食事代で9000円",
                "お客様との食事で8500円",
                "外部との会食で8000円",
                "取引先との食事で9500円"
            ],
            'RULE_015': [
                "高額な外部食事代で15000円",
                "お客様との高級会食で12000円",
                "外部との高額食事で18000円",
                "取引先との高級食事で20000円"
            ],
            'RULE_016': [
                "社内メンバーのみの食事で5000円",
                "部署の懇親会で4500円",
                "社内ランチで3000円",
                "チームビルディング食事で4000円"
            ],
            'RULE_017': [
                "社内メンバーの食事（8%）で3000円",
                "部署の懇親会（8%）で2500円",
                "社内ランチ（8%）で2000円",
                "チームビルディング食事（8%）で3500円"
            ],
            'RULE_018': [
                "お客様へのお土産で3000円",
                "取引先への贈り物で5000円",
                "お客様への記念品で4000円",
                "取引先へのお土産で3500円"
            ],
            'RULE_019': [
                "お客様へのお土産（8%）で5000円",
                "取引先への贈り物（8%）で3500円",
                "お客様への記念品（8%）で4000円",
                "取引先へのお土産（8%）で4500円"
            ],
            'RULE_020': [
                "セブンイレブンでコピー代100円",
                "ファミマでコピー代150円",
                "コンビニコピー代で200円",
                "コピーサービスで120円"
            ],
            'RULE_021': [
                "ペン購入で100円",
                "紙10冊で500円",
                "文房具購入で300円",
                "オフィス用品で800円"
            ],
            'RULE_022': [
                "ノートPC購入で150000円",
                "プロジェクター購入で120000円",
                "高額機器購入で180000円",
                "設備購入で160000円"
            ],
            'RULE_023': [
                "朝日新聞購読で4000円",
                "ニューヨークタイムズ購読で5000円",
                "新聞購読料で3500円",
                "雑誌購読で2500円"
            ],
            'RULE_024': [
                "海外新聞購読で3000円",
                "海外雑誌購読で2000円",
                "海外メディア購読で4000円",
                "国際新聞購読で3500円"
            ],
            'RULE_025': [
                "Freee会計ソフトで16500円",
                "Zoom利用料で2000円",
                "SaaS利用料で15000円",
                "クラウドサービスで12000円"
            ],
            'RULE_026': [
                "TestRail利用料で10000円",
                "Dropbox利用料で5000円",
                "海外SaaS利用料で8000円",
                "国際サービス利用料で7000円"
            ],
            'RULE_027': [
                "切手代で84円",
                "宅配便代で1500円",
                "郵送料で200円",
                "配送料で800円"
            ],
            'RULE_028': [
                "レターパック代で370円",
                "はがき代で85円",
                "国内郵送料で150円",
                "郵便料金で200円"
            ],
            'RULE_029': [
                "バイク便で1500円",
                "宅配便で800円",
                "国内配送で1200円",
                "配達料で1000円"
            ],
            'RULE_030': [
                "EMS国際郵便で1500円",
                "DHL国際配送で2000円",
                "海外郵送料で1800円",
                "国際配送で2200円"
            ]
        }
    
    def generate_rule_examples(self, rule_id: str, rule_description: str) -> List[str]:
        """Generate JSON examples for a specific rule."""
        # Check if we have predefined patterns - convert to JSON format
        if rule_id in self.expense_patterns:
            return [self._text_to_json(text, rule_id) for text in self.expense_patterns[rule_id]]
        
        # Generate JSON examples based on rule description
        examples = []
        
        # Extract key terms from rule description and create JSON
        if "電車" in rule_description or "バス" in rule_description:
            examples.extend([
                self._create_travel_json("電車", "東京", "新宿", "500"),
                self._create_travel_json("バス", "大阪", "京都", "300"),
                self._create_travel_json("電車", "渋谷", "新宿", "800")
            ])
        elif "新幹線" in rule_description or "飛行機" in rule_description:
            examples.extend([
                self._create_travel_json("新幹線", "東京", "大阪", "15000"),
                self._create_travel_json("飛行機", "東京", "福岡", "25000"),
                self._create_travel_json("新幹線", "東京", "名古屋", "30000")
            ])
        elif "タクシー" in rule_description:
            examples.extend([
                self._create_taxi_json("会議のため", "3000"),
                self._create_taxi_json("緊急時", "2500"),
                self._create_taxi_json("お客様訪問", "4000")
            ])
        elif "会議" in rule_description or "セミナー" in rule_description:
            examples.extend([
                self._create_meeting_json("会議", "50000"),
                self._create_meeting_json("セミナー", "30000"),
                self._create_meeting_json("研修", "40000")
            ])
        elif "食事" in rule_description or "会食" in rule_description:
            examples.extend([
                self._create_meal_json("お客様との食事", "8000"),
                self._create_meal_json("取引先との会食", "12000"),
                self._create_meal_json("ビジネス食事", "6000")
            ])
        elif "購入" in rule_description:
            examples.extend([
                self._create_purchase_json("文房具", "5000"),
                self._create_purchase_json("オフィス用品", "8000"),
                self._create_purchase_json("設備", "3000")
            ])
        else:
            # Generic expense JSON
            examples.extend([
                self._create_generic_json("ビジネス費用", "5000"),
                self._create_generic_json("業務関連費用", "8000"),
                self._create_generic_json("業務活動費", "6000")
            ])
        
        return examples[:4]  # Return up to 4 examples
    
    def _text_to_json(self, text: str, rule_id: str) -> str:
        """Convert Japanese text to JSON format matching the actual data structure."""
        # Extract amount from text if possible
        import re
        amount_match = re.search(r'(\d+)円', text)
        amount = amount_match.group(1) if amount_match else "500"
        
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": self._get_category_for_rule(rule_id),
            "amount": amount,
            "date": "2025-01-01",
            "description": text,
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _get_category_for_rule(self, rule_id: str) -> str:
        """Get the category name for a rule ID."""
        # Map rule IDs to their Japanese category names
        category_map = {
            'RULE_001': '旅費交通費：(国内)近隣の電車・バスのみ',
            'RULE_002': '旅費交通費：(国内)新幹線・飛行機・宿泊',
            'RULE_003': '旅費交通費：(海外)近隣の電車・バス',
            'RULE_004': '旅費交通費：(海外)新幹線・飛行機・宿泊',
            'RULE_005': '旅費交通費：(国内)タクシー',
            'RULE_006': '旅費交通費：(海外)タクシー',
            'RULE_007': '旅費交通費：(国内)接待タクシー',
            'RULE_008': '旅費交通費：(国内)日当',
            'RULE_009': '旅費交通費：(海外)日当',
            'RULE_010': '旅費交通費：宿泊税・入湯税',
            'RULE_011': '旅費交通費：高速道路ETC',
            'RULE_012': '会議費',
            'RULE_013': '会議費（8%）',
            'RULE_014': '交際費：外部との食事',
            'RULE_015': '交際費：外部との高額食事',
            'RULE_016': '交際費：社内メンバーのみの食事',
            'RULE_017': '交際費：社内メンバーの食事（8%）',
            'RULE_018': '交際費：お客様へのお土産',
            'RULE_019': '交際費：お客様へのお土産（8%）',
            'RULE_020': '通信費：コピー代',
            'RULE_021': '消耗品費：文房具',
            'RULE_022': '消耗品費：高額機器',
            'RULE_023': '通信費：新聞購読',
            'RULE_024': '通信費：海外新聞購読',
            'RULE_025': '通信費：SaaS利用料',
            'RULE_026': '通信費：海外SaaS利用料',
            'RULE_027': '通信費：郵送料',
            'RULE_028': '通信費：国内郵送料',
            'RULE_029': '通信費：国内配送',
            'RULE_030': '通信費：海外配送'
        }
        return category_map.get(rule_id, 'その他経費')
    
    def _create_travel_json(self, transport_mode: str, origin: str, destination: str, amount: str) -> str:
        """Create travel expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "旅費交通費：(国内)近隣の電車・バスのみ",
            "amount": amount,
            "date": "2025-01-01",
            "description": f"入 {origin} 出 {destination}",
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _create_taxi_json(self, reason: str, amount: str) -> str:
        """Create taxi expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "旅費交通費：(国内)タクシー",
            "amount": amount,
            "date": "2025-01-01",
            "description": f"タクシー代 {reason}",
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _create_meeting_json(self, meeting_type: str, amount: str) -> str:
        """Create meeting expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "会議費",
            "amount": amount,
            "date": "2025-01-01",
            "description": f"{meeting_type}参加費",
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _create_meal_json(self, meal_type: str, amount: str) -> str:
        """Create meal expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "交際費：外部との食事",
            "amount": amount,
            "date": "2025-01-01",
            "description": f"{meal_type}代",
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _create_purchase_json(self, item: str, amount: str) -> str:
        """Create purchase expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "消耗品費：文房具",
            "amount": amount,
            "date": "2025-01-01",
            "description": f"{item}購入",
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def _create_generic_json(self, description: str, amount: str) -> str:
        """Create generic expense JSON matching Japanese data structure."""
        return json.dumps({
            "number": f"JP{random.randint(100000, 999999)}",
            "category": "その他経費",
            "amount": amount,
            "date": "2025-01-01",
            "description": description,
            "memo": "",
            "payment_input_method": "account",
            "receipt_type": "Unknown",
            "receipt_text": ""
        }, ensure_ascii=False)
    
    def generate_training_data(self, min_examples_per_rule: int = 2) -> List[Dict[str, Any]]:
        """Generate training data from all rules."""
        training_data = []
        rules_with_insufficient_examples = []
        
        print("Generating Japanese synthetic training data...")
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Processing rules"):
            rule_id = row['Rule']
            rule_description = row.get('経費科目名称\n（クラウド経費に登録されている名称）', '')
            
            # Generate examples for this rule
            examples = self.generate_rule_examples(rule_id, rule_description)
            
            # Ensure minimum number of examples
            if len(examples) < min_examples_per_rule:
                rules_with_insufficient_examples.append((rule_id, len(examples)))
                # Generate additional examples
                additional_examples = self._generate_additional_japanese_examples(rule_id, rule_description, min_examples_per_rule - len(examples))
                examples.extend(additional_examples)
            
            for example in examples:
                training_data.append({
                    'text': example,
                    'rule_id': rule_id,
                    'rule_description': rule_description
                })
        
        # Report rules with insufficient examples
        if rules_with_insufficient_examples:
            print(f"\nWarning: {len(rules_with_insufficient_examples)} rules had insufficient examples:")
            for rule_id, count in rules_with_insufficient_examples:
                print(f"  {rule_id}: {count} examples (generated additional)")
                
        return training_data
    
    def _generate_additional_japanese_examples(self, rule_id: str, rule_description: str, num_needed: int) -> List[str]:
        """Generate additional Japanese examples for rules with insufficient examples."""
        additional_examples = []
        
        for i in range(num_needed):
            synthetic_text = self._create_additional_japanese_example(rule_id, rule_description, i)
            if synthetic_text:
                additional_examples.append(synthetic_text)
        
        return additional_examples
    
    def _create_additional_japanese_example(self, rule_id: str, rule_description: str, variation: int) -> str:
        """Create additional Japanese synthetic JSON examples."""
        # Generate JSON variations based on rule type
        if "電車" in rule_description or "バス" in rule_description:
            variations = [
                self._create_travel_json("電車", "駅A", "駅B", str(500 + variation * 100)),
                self._create_travel_json("バス", "都市A", "都市B", str(300 + variation * 50)),
                self._create_travel_json("電車", "場所A", "場所B", str(400 + variation * 75))
            ]
        elif "新幹線" in rule_description or "飛行機" in rule_description:
            variations = [
                self._create_travel_json("新幹線", "東京", "大阪", str(15000 + variation * 2000)),
                self._create_travel_json("飛行機", "東京", "福岡", str(25000 + variation * 3000)),
                self._create_travel_json("新幹線", "都市A", "都市B", str(20000 + variation * 2500))
            ]
        elif "タクシー" in rule_description:
            variations = [
                self._create_taxi_json("会議のため", str(3000 + variation * 500)),
                self._create_taxi_json("緊急時", str(2500 + variation * 400)),
                self._create_taxi_json("お客様訪問", str(3500 + variation * 600))
            ]
        elif "会議" in rule_description or "セミナー" in rule_description:
            variations = [
                self._create_meeting_json("会議", str(50000 + variation * 10000)),
                self._create_meeting_json("セミナー", str(30000 + variation * 5000)),
                self._create_meeting_json("研修", str(40000 + variation * 7500))
            ]
        elif "食事" in rule_description or "会食" in rule_description:
            variations = [
                self._create_meal_json("お客様との食事", str(8000 + variation * 1000)),
                self._create_meal_json("取引先との会食", str(12000 + variation * 1500)),
                self._create_meal_json("ビジネス食事", str(6000 + variation * 800))
            ]
        else:
            # Generic expense JSON
            variations = [
                self._create_generic_json("ビジネス費用", str(5000 + variation * 1000)),
                self._create_generic_json("業務関連費用", str(8000 + variation * 1500)),
                self._create_generic_json("業務活動費", str(6000 + variation * 1200))
            ]
        
        return variations[variation % len(variations)]
    
    def save_training_data(self, output_path: str):
        """Save training data to JSON file."""
        training_data = self.generate_training_data()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
            
        print(f"Generated {len(training_data)} Japanese training examples")
        print(f"Saved to {output_path}")
        
        # Print statistics
        rule_counts = {}
        for item in training_data:
            rule_id = item['rule_id']
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            
        print(f"\nExamples per rule:")
        for rule_id, count in sorted(rule_counts.items()):
            print(f"  {rule_id}: {count} examples")


