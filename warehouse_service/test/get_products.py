import requests
import json
from typing import List, Dict
import sys

def get_products_from_api() -> List[Dict]:
    """
    Отправляет GET запрос к API и получает список товаров
    """
    try:
        print("🔄 Отправка запроса к API...")
        
        response = requests.get(
            'http://localhost:8000/',
            headers={'accept': 'application/json'},
            timeout=10
        )
        
        # Проверяем статус ответа
        response.raise_for_status()
        
        print(f"✅ Запрос успешен! Статус: {response.status_code}")
        return response.json()
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения: Не удалось соединиться с сервером")
        print("   Убедитесь, что сервер запущен на http://localhost:8000/")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса: Сервер не ответил вовремя")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

def display_products_summary(products: List[Dict]):
    """
    Выводит общую статистику по товарам
    """
    print("\n" + "=" * 80)
    print("📦 ОБЩАЯ СТАТИСТИКА")
    print("=" * 80)
    print(f"Всего товаров получено: {len(products)}")
    
    # Статистика по категориям
    categories = {}
    for product in products:
        category = product.get('category_name', 'Неизвестно')
        categories[category] = categories.get(category, 0) + 1
    
    print("📊 Распределение по категориям:")
    for category, count in categories.items():
        print(f"   • {category}: {count} товаров")
    
    # Общая аналитика
    total_quantity = sum(product['total_quantity'] for product in products)
    total_value = sum(product['base_price'] * product['total_quantity'] for product in products)
    active_products = sum(1 for product in products if product['is_active'])
    
    print(f"\n💰 Финансовая статистика:")
    print(f"   • Общее количество единиц: {total_quantity} шт.")
    print(f"   • Общая стоимость inventory: ${total_value:,.2f}")
    print(f"   • Активных товаров: {active_products} из {len(products)}")
    
    # Экстремумы
    if products:
        most_expensive = max(products, key=lambda x: x['base_price'])
        cheapest = min(products, key=lambda x: x['base_price'])
        most_quantity = max(products, key=lambda x: x['total_quantity'])
        least_quantity = min(products, key=lambda x: x['total_quantity'])
        
        print(f"\n🎯 Экстремумы:")
        print(f"   • Самый дорогой: '{most_expensive['name']}' - ${most_expensive['base_price']}")
        print(f"   • Самый дешевый: '{cheapest['name']}' - ${cheapest['base_price']}")
        print(f"   • Больше всего на складе: '{most_quantity['name']}' - {most_quantity['total_quantity']} шт.")
        print(f"   • Меньше всего на складе: '{least_quantity['name']}' - {least_quantity['total_quantity']} шт.")

def display_detailed_products(products: List[Dict]):
    """
    Детальный вывод каждого товара
    """
    print("\n" + "=" * 80)
    print("📋 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ТОВАРАХ")
    print("=" * 80)
    
    for i, product in enumerate(products, 1):
        print(f"\n🏷️  ТОВАР #{i}")
        print(f"   ID: {product['id']}")
        print(f"   Название: {product['name']}")
        print(f"   Категория: {product['category_name']}")
        print(f"   Цена: ${product['base_price']}")
        print(f"   Количество: {product['total_quantity']} шт.")
        print(f"   SKU: {product['sku'] or 'Не указан'}")
        print(f"   Активен: {'✅ Да' if product['is_active'] else '❌ Нет'}")
        print(f"   Создан: {product['created_at']}")
        
        # Вывод специфичных атрибутов
        category = product['category_name']
        has_attributes = False
        
        if category == 'Термокружки':
            attrs = ['volume_ml', 'color', 'brand', 'material']
            for attr in attrs:
                if product.get(attr):
                    print(f"   {attr.replace('_', ' ').title()}: {product[attr]}")
                    has_attributes = True
                    
        elif category == 'Серверы':
            attrs = ['ram_gb', 'cpu_model', 'cpu_cores', 'form_factor', 'manufacturer']
            for attr in attrs:
                if product.get(attr):
                    print(f"   {attr.replace('_', ' ').title()}: {product[attr]}")
                    has_attributes = True
        
        if not has_attributes:
            print(f"   ⚠️  Специфичные атрибуты: не заполнены")
        
        print("-" * 50)

def display_products_table(products: List[Dict]):
    """
    Краткий табличный вывод
    """
    print("\n" + "=" * 80)
    print("📊 ТАБЛИЧНЫЙ ВЫВОД")
    print("=" * 80)
    
    print(f"{'ID':<3} {'Кат.':<4} {'Название':<35} {'Цена':<8} {'Кол-во':<6} {'SKU':<15}")
    print("-" * 80)
    
    for product in products:
        category_icon = "☕" if "Термокруж" in product['category_name'] else "🖥️"
        name = product['name'][:33] + "..." if len(product['name']) > 33 else product['name']
        sku = product['sku'] or "—"
        
        print(f"{product['id']:<3} {category_icon:<4} {name:<35} "
              f"${product['base_price']:<7.2f} {product['total_quantity']:<6} {sku:<15}")

def save_products_to_file(products: List[Dict], filename: str = "products_output.json"):
    """
    Сохраняет полученные данные в файл
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Данные сохранены в файл: {filename}")
        print(f"   Всего записей: {len(products)}")
        
    except Exception as e:
        print(f"❌ Ошибка при сохранении в файл: {e}")

def main():
    """
    Основная функция - выполняет весь процесс от запроса до вывода
    """
    print("🚀 ЗАПУСК ПРОЦЕССА ПОЛУЧЕНИЯ И АНАЛИЗА ДАННЫХ О ТОВАРАХ")
    print("=" * 80)
    
    # 1. Получаем данные от API
    products = get_products_from_api()
    
    if not products:
        print("❌ Получен пустой список товаров")
        return
    
    # 2. Выводим общую статистику
    display_products_summary(products)
    
    # 3. Выводим табличный обзор
    display_products_table(products)
    
    # 4. Выводим детальную информацию
    display_detailed_products(products)
    
    # 5. Сохраняем в файл
    save_products_to_file(products)
    
    print("\n" + "=" * 80)
    print("✅ ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!")
    print("=" * 80)

if __name__ == "__main__":
    main()