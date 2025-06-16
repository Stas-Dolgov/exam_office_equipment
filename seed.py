from datetime import date
from app import db, Category, Equipment, Photo 
import hashlib


def generate_md5(filename):
    """Генерирует MD5 хэш для указанного файла."""
    md5_hash = hashlib.md5()
    try:
        with open(filename, "rb") as f:  # Открываем файл в бинарном режиме
            for chunk in iter(lambda: f.read(4096), b""):  # 4096 байт - размер чанка
                md5_hash.update(chunk)
        return md5_hash.hexdigest()  # Возвращаем хэш в шестнадцатеричном формате
    except FileNotFoundError:
        print(f"Файл не найден: {filename}")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def seed_database():
    # Очистка существующих данных
    db.session.query(Equipment).delete()
    db.session.query(Category).delete()
    db.session.query(Photo).delete()
    db.session.commit()

    # Создание категорий
    category1 = Category(name='Компьютеры', description='Настольные компьютеры и ноутбуки')
    category2 = Category(name='Принтеры', description='Лазерные и струйные принтеры')
    category3 = Category(name='Сканеры', description='Планшетные и потоковые сканеры')
    category4 = Category(name='Телефоны', description='IP и аналоговые телефоны')
    category5 = Category(name='Мониторы', description='')

    # Создание фотографий
    photo1 = Photo(filename='static/images/computer1.png', mime_type='image/png', md5_hash=generate_md5('static/images/computer1.png'))
    photo2 = Photo(filename='static/images/computer2.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/computer2.jpg'))
    photo3 = Photo(filename='static/images/printer1.png', mime_type='image/png', md5_hash=generate_md5('static/images/printer1.png'))
    photo4 = Photo(filename='static/images/printer2.jpg', mime_type='image/jpg', md5_hash=generate_md5('static/images/printer2.jpg'))
    photo5 = Photo(filename='static/images/scanner1.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/scanner1.jpg'))
    photo6 = Photo(filename='static/images/scanner2.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/scanner2.jpg'))
    photo7 = Photo(filename='static/images/phone1.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/phone1.jpg'))
    photo8 = Photo(filename='static/images/phone2.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/phone2.jpg'))
    photo9 = Photo(filename='static/images/monitor1.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/monitor1.jpg'))
    photo10 = Photo(filename='static/images/monitor2.jpg', mime_type='image/jpeg', md5_hash=generate_md5('static/images/monitor2.jpg'))

    # Компьютеры
    equipment1 = Equipment(name='Мини ПК INFERIT', inventory_number='COMP001', category=category1, purchase_date=date(2025, 5, 1), cost=9200.00, status='В эксплуатации', photo_id=photo1.id)
    equipment2 = Equipment(name='Мини ПК Beelink T5', inventory_number='COMP002', category=category1, purchase_date=date(2025, 5, 1), cost=9500.00, status='В эксплуатации', photo_id=photo2.id)
    equipment3 = Equipment(name='Мини ПК INFERIT', inventory_number='COMP003', category=category1, purchase_date=date(2025, 5, 15), cost=9100.00, status='В эксплуатации', photo_id=photo1.id)
    equipment4 = Equipment(name='Мини ПК INFERIT', inventory_number='COMP004', category=category1, purchase_date=date(2025, 5, 15), cost=9100.00, status='Списано', photo_id=photo1.id)
    equipment5 = Equipment(name='Мини ПК Beelink T5', inventory_number='COMP005', category=category1, purchase_date=date(2025, 5, 15), cost=9300.00, status='В эксплуатации', photo_id = photo2.id)

    # Принтеры
    equipment6 = Equipment(name='Hp LaserJet M141w', inventory_number='PRNT001', category = category2, purchase_date = date(2025, 1, 1), cost = 9400.00, status = 'В эксплуатации', photo_id = photo3.id)
    equipment7 = Equipment(name='Hp LaserJet M141w', inventory_number = 'PRNT002', category = category2, purchase_date = date(2025, 2, 1), cost = 9450.00, status = 'В эксплуатации', photo_id = photo3.id)
    equipment8 = Equipment(name='МФУ Deli D511W', inventory_number = 'PRNT003', category = category2, purchase_date = date(2025, 3, 1), cost = 9500.00, status = 'В эксплуатации', photo_id = photo4.id)
    equipment9 = Equipment(name='МФУ Deli D511W', inventory_number = 'PRNT004', category = category2, purchase_date = date(2025, 4, 1), cost = 9350.00, status = 'На ремонте', photo_id = photo4.id)
    equipment10 = Equipment(name='Hp LaserJet M141w', inventory_number = 'PRNT005', category = category2, purchase_date = date(2025, 5, 1), cost = 9300.00, status = 'Списано', photo_id = photo3.id)

    # Сканеры
    equipment11 = Equipment(name = 'Сканер Canon CanoScan LiDE 400', inventory_number = 'SCAN001', category = category3, purchase_date = date(2025, 1, 1), cost = 8250.00, status = 'В эксплуатации', photo_id = photo5.id)
    equipment12 = Equipment(name = 'Сканер Canon CanoScan LiDE 400', inventory_number = 'SCAN002', category = category3, purchase_date = date(2025, 2, 1), cost = 8300.00, status = 'В эксплуатации', photo_id = photo5.id)
    equipment13 = Equipment(name = 'Сканер Canon CanoScan LiDE 400', inventory_number = 'SCAN003', category = category3, purchase_date = date(2025, 3, 1), cost = 8350.00, status = 'В эксплуатации', photo_id = photo5.id)
    equipment14 = Equipment(name = 'Сканер Canon CanoScan LiDE 300', inventory_number = 'SCAN004', category = category3, purchase_date = date(2025, 4, 1), cost = 8200.00, status = 'На ремонте', photo_id = photo6.id)
    equipment15 = Equipment(name = 'Сканер Canon CanoScan LiDE 300', inventory_number = 'SCAN005', category = category3, purchase_date = date(2025, 5, 1), cost = 8100.00, status = 'Списано', photo_id = photo6.id)

    # Телефоны
    equipment16 = Equipment(name = 'Телефон Cisco CP-7821-K9', inventory_number = 'PHON001', category = category4, purchase_date = date(2025, 1, 1), cost = 3100.00, status = 'В эксплуатации', photo_id = photo7.id)
    equipment17 = Equipment(name = 'Телефон Cisco CP-7821-K9', inventory_number = 'PHON002', category = category4, purchase_date = date(2025, 2, 1), cost = 3150.00, status = 'В эксплуатации', photo_id = photo7.id)
    equipment18 = Equipment(name = 'Телефон Cisco CP-7821-K9', inventory_number = 'PHON003', category = category4, purchase_date = date(2025, 3, 1), cost = 3120.00, status = 'В эксплуатации', photo_id = photo7.id)
    equipment19 = Equipment(name = 'Телефон Cisco CP-7821-K9', inventory_number = 'PHON004', category = category4, purchase_date = date(2025, 4, 1), cost = 3090.00, status = 'На ремонте', photo_id = photo7.id)
    equipment20 = Equipment(name = 'Телефон Cisco Unified SIP Phone CP-3905', inventory_number = 'PHON005', category = category4, purchase_date = date(2025, 5, 1), cost = 3080.00, status = 'В эксплуатации', photo_id = photo8.id)

    # Мониторы
    equipment21 = Equipment(name = 'Монитор Carrera 23,8', inventory_number = 'MONI001', category = category5, purchase_date = date(2025, 1, 1), cost = 8300.00, status = 'В эксплуатации', photo_id = photo9.id)
    equipment22 = Equipment(name = 'Монитор Carrera 23,8', inventory_number = 'MONI002', category = category5, purchase_date = date(2025, 2, 1), cost = 8350.00, status = 'В эксплуатации', photo_id = photo9.id)
    equipment23 = Equipment(name = 'Монитор Carrera 23,8', inventory_number = 'MONI003', category = category5, purchase_date = date(2025, 3, 1), cost = 8400.00, status = 'В эксплуатации', photo_id = photo9.id)
    equipment24 = Equipment(name = 'Монитор Carrera 23,8', inventory_number = 'MONI004', category = category5, purchase_date = date(2025, 4, 1), cost = 8450.00, status = 'На ремонте', photo_id = photo9.id)
    equipment25 = Equipment(name = 'Монитор LG 27', inventory_number = 'MONI005', category = category5, purchase_date = date(2025, 5, 1), cost = 9250.00, status = 'Списано', photo_id = photo10.id)

    # Добавление объектов в сессию и сохранение
    db.session.add_all([category1, category2, category3, category4, category5,
                        photo1, photo2, photo3, photo4, photo5, photo6, photo7, 
                        photo8, photo9, photo10,
                        equipment1, equipment2, equipment3, equipment4, equipment5,
                        equipment6, equipment7, equipment8, equipment9, equipment10,
                        equipment11, equipment12, equipment13, equipment14, equipment15,
                        equipment16, equipment17, equipment18, equipment19, equipment20,
                        equipment21, equipment22, equipment23, equipment24, equipment25])
    db.session.commit()

if __name__ == '__main__':
    from app import app
    with app.app_context():
        seed_database()
        print('База данных заполнена!')