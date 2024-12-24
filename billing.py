from db import db, User, Invoice, Customer, Stock, DailyStock
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
import plotly.graph_objs as go
import plotly.io as pio
from dateutil.relativedelta import relativedelta


class GetInvoice:
    @staticmethod
    def get_invoice_details(invoice_no):
        results = db.session.execute(db.select(Invoice).where(Invoice.invoice_no == invoice_no))
        invoice_detail = results.scalar()
        return invoice_detail


    @staticmethod
    def save_invoice(customer_data, goods_details, total_amount):
        todays_date = f"{datetime.now().day}/{datetime.now().month}/{datetime.now().year}"
        date = datetime.strptime(todays_date, '%d/%m/%Y').date()
        RPG15KG = 0
        RPG15LTR = 0
        RPG13KG = 0
        other = 0
        total_no_tins = 0
        total_quantity = 0
        for goods in goods_details:
            if goods['description'] == "RICH PALM GOLD 15 KG TIN":
                RPG15KG += int(goods['quantity'])
                total_no_tins += int(goods['quantity'])
                total_quantity += RPG15KG * 15
            elif goods['description'] == "RICH PALM GOLD 15 LTR TIN":
                RPG15LTR += int(goods['quantity'])
                total_no_tins += int(goods['quantity'])
                total_quantity += RPG15LTR * 13.5

            elif goods['description'] == "RICH PALM GOLD 13 KG TIN":
                RPG13KG += int(goods['quantity'])
                total_no_tins += int(goods['quantity'])
                total_quantity += RPG13KG * 13
            else:
                other += int(goods['quantity'])
                total_no_tins += int(goods['quantity'])
        try:
            new_entry = Invoice(invoice_no=int(customer_data['invoice_no']), customer_details=customer_data,
                                goods_details=goods_details, total_amount=total_amount, date=date)
            db.session.add(new_entry)
            db.session.commit()
            daily_stock_update = DailyStock(name=customer_data['customer_name'],
                                      tins = {
                                          "RPG15KG": RPG15KG,
                                          "RPG15LTR": RPG15LTR,
                                          "RPG13KG": RPG13KG
                                      },
                                      total_quantity=total_quantity,
                                      date=date
                                      )
            db.session.add(daily_stock_update)
            db.session.commit()

            Stocks.update_stock(total_quantity, total_no_tins, "deduct")
            print("Data saved successfully!")
            return  "Data saved successfully!"
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the transaction if there's an error
            return f"Failed to save data"

    @staticmethod
    def get_all_invoices():

        # invoices = db.session.query(Invoice).filter(Invoice.id == 12).first()
        invoices = db.session.query(Invoice).all()
        return invoices

    @staticmethod
    def update_invoice(invoice_no, name, amount, status):
        result = db.session.execute(db.select(Invoice).where(Invoice.invoice_no == invoice_no))
        invoice = result.scalar()
        print(invoice.total_amount)
        if name:
            new_amount = invoice.total_amount
            edit_name = invoice.customer_details
            edit_name = {
                "customer_name": name,
                "cust_gst": edit_name['cust_gst'],
                "eway_bill": edit_name['eway_bill'],
                "invoice_no": edit_name['invoice_no']
            }
            new_amount = {
                "total_quantity": new_amount['total_quantity'],
                "total_sgst": new_amount['total_sgst'],
                "total_amount": new_amount['total_amount'],
                "overall_amount": amount,
                "amnt_in_words": new_amount['amnt_in_words'],
                "status": status
            }
            invoice.total_amount = new_amount
            invoice.customer_details = edit_name
            db.session.commit()
            return "Invoice Updated"
        else:
            if invoice.total_amount['status'] == "pending":
                new_amount = invoice.total_amount
                new_amount = {
                    "total_quantity": new_amount['total_quantity'],
                    "total_sgst": new_amount['total_sgst'],
                    "total_amount": new_amount['total_amount'],
                    "overall_amount": new_amount['overall_amount'],
                    "amnt_in_words": new_amount['amnt_in_words'],
                    "status": status
                }
                invoice.total_amount = new_amount
                db.session.commit()
                return "Invoice Updated"
            else:
                return "Invoice in not updated check status"



class Customers:
    @staticmethod
    def get_all_customers():
        result = db.session.query(Customer).all()
        names = []
        gst_no = []
        for name in result:
            names.append(name.customer_name)
            gst_no.append(name.gst_no)
        return names


    @staticmethod
    def add_customer(customer_name, gstn):
        new_cust = Customer(
            customer_name = customer_name,
            gst_no=gstn,
        )
        db.session.add(new_cust)
        db.session.commit()

        return f"Customer {customer_name} Added"


class Report:
    @staticmethod
    def monthly_report(month):
        response = GetInvoice.get_all_invoices()
        stocks = db.session.query(DailyStock).all()
        total_oil = 0
        for stock in stocks:
            if stock.date.strftime("%B") == month:
                total_oil += int(stock.total_quantity)
        this_month_invoices = []
        cust_list = []
        total_amount = 0
        RPG15KG = 0
        RPG15LTR = 0
        RPG13KG = 0
        HG15KG = 0
        HG15LTR = 0
        for invoice in response:
            if invoice.date.strftime("%B") == month:
                this_month_invoices.append(invoice)
        custs_list = []
        for invoice in this_month_invoices:
            total_amount += int(invoice.total_amount['overall_amount'])
            if invoice.customer_details['customer_name'] not in custs_list:
                custs_list.append(invoice.customer_details['customer_name'])
            for desc in invoice.goods_details:
                if desc['description'] == "RICH PALM GOLD 15 KG TIN":
                    RPG15KG += int(desc['quantity'])
                elif desc['description'] == "RICH PALM GOLD 15 LTR TIN":
                    RPG15LTR += int(desc['quantity'])
                elif desc['description'] == "RICH PALM GOLD 13 KG TIN":
                    RPG13KG += int(desc['quantity'])
                elif desc['description'] == "HEALTHY GOLD 15 KG TIN":
                    HG15KG += int(desc['quantity'])
                elif desc['description'] == "HEALTHY GOLD 15 LTR TIN":
                    HG15LTR += int(desc['quantity'])
        cust_list.append(custs_list)
        tins_desc = ['RPG15KG', 'RPG15LTR', 'RPG13KG', 'HG15KG', 'HG15LTR']
        no_of_tins = [RPG15KG, RPG15LTR, RPG13KG, HG15KG, HG15LTR]
        total_tins = RPG15KG + RPG15LTR + RPG13KG + HG15KG + HG15LTR
        months = [month]
        totals = [total_amount]

        # Create Plotly bar chart
        bar_chart = go.Figure(
            data=[
                go.Bar(
                    x=tins_desc,
                    y=no_of_tins,
                    marker=dict(color='rgba(54, 162, 235, 0.7)'),
                    name="Sales"
                )
            ],
            layout=go.Layout(
                title=f"Total No Of Tins in month of {month}: {total_tins}",
                yaxis=dict(title="TIN's in quantity"),
                height=500,
            )
        )
        # Render chart as HTML
        chart_html = pio.to_html(bar_chart, full_html=False)
        return chart_html, cust_list, totals, months, total_oil


    @staticmethod
    def six_month_report():
        response = GetInvoice.get_all_invoices()
        current_date = datetime.now()
        months = [(current_date - relativedelta(months=i)).strftime('%B') for i in range(6)]
        months = months[::-1]

        first_month = 0
        first_month_custlist = []
        second_month = 0
        second_month_custlist = []
        third_moth = 0
        third_month_custlist = []
        fourth_month = 0
        fourth_month_custlist = []
        fifth_month = 0
        fifth_month_custlist = []
        sixth_month = 0
        sixth_month_custlist = []

        for invoice in response:
            if invoice.date.strftime("%B") == months[0]:
                first_month += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in first_month_custlist:
                    first_month_custlist.append(invoice.customer_details['customer_name'])
            elif invoice.date.strftime("%B") == months[1]:
                second_month += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in second_month_custlist:
                    second_month_custlist.append(invoice.customer_details['customer_name'])
            elif invoice.date.strftime("%B") == months[2]:
                third_moth += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in third_month_custlist:
                    third_month_custlist.append(invoice.customer_details['customer_name'])
            elif invoice.date.strftime("%B") == months[3]:
                fourth_month += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in fourth_month_custlist:
                    fourth_month_custlist.append(invoice.customer_details['customer_name'])
            elif invoice.date.strftime("%B") == months[4]:
                fifth_month += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in fifth_month_custlist:
                    fifth_month_custlist.append(invoice.customer_details['customer_name'])
            elif invoice.date.strftime("%B") == months[5]:
                sixth_month += int(invoice.total_amount['overall_amount'])
                if invoice.customer_details['customer_name'] not in sixth_month_custlist:
                    sixth_month_custlist.append(invoice.customer_details['customer_name'])

        totals = [first_month, second_month, third_moth, fourth_month, fifth_month, sixth_month]
        cust_list = [first_month_custlist, second_month_custlist, third_month_custlist, fourth_month_custlist, fifth_month_custlist, sixth_month_custlist]

        # Create Plotly bar chart
        bar_chart = go.Figure(
            data=[
                go.Bar(
                    x=months,
                    y=totals,
                    marker=dict(color='rgba(54, 162, 235, 0.7)'),
                    name="Sales"
                )
            ],
            layout=go.Layout(
                title=f"Sale report of last six months",
                yaxis=dict(title="sales in Rupees"),
                height=500,
            )
        )
        # Render chart as HTML
        chart_html = pio.to_html(bar_chart, full_html=False)
        return chart_html, cust_list, totals, months



class Stocks:

    @staticmethod
    def get_stock():
        # result = db.session.query(Stock).filter_by(id=1).first()
        latest = db.session.query(Stock).order_by(Stock.date.desc()).first()
        if latest.date == datetime.today().date():
            return latest
        else:
            new_stock = Stock(
                oil={
                    "today_opening_stock": latest.oil['RPG'],
                    "RPG": latest.oil['RPG']
                },
                tins_in_stock=latest.tins_in_stock,
                other={
                    "caps": latest.other['caps']
                },
                date=datetime.today().date()
            )
            db.session.add(new_stock)
            db.session.commit()
            latest = db.session.query(Stock).order_by(Stock.date.desc()).first()
            return latest


    @staticmethod
    def update_stock(quantity, no_of_tins, method):
        result = db.session.query(Stock).order_by(Stock.date.desc()).first()
        update_quantity = result.oil
        print(update_quantity)

        if method == "add":
            result.tins_in_stock += no_of_tins
            update_quantity = {
                'today_opening_stock': update_quantity['today_opening_stock'],
                'RPG': float(update_quantity['RPG']) + quantity
            }
        elif method == "deduct":
            result.tins_in_stock -= no_of_tins
            update_quantity = {
                'today_opening_stock': update_quantity['today_opening_stock'],
                'RPG': float(update_quantity['RPG']) - quantity
            }

        result.oil = update_quantity
        db.session.commit()

    @staticmethod
    def get_all_daily_stocks():
        total_tins = 0
        KG15 = 0
        LTR15 = 0
        KG13 = 0
        result = db.session.query(DailyStock).filter(DailyStock.date == datetime.today().date()).all()
        for today in result:
            KG15 += int(today.tins['RPG15KG'])
            LTR15 += int(today.tins['RPG15LTR'])
            KG13 += int(today.tins['RPG13KG'])
            total_tins += int(today.tins['RPG15KG']) + int(today.tins['RPG15LTR']) + int(today.tins['RPG13KG'])

        tis_count = {
            "total_tins": total_tins,
            "15KG": KG15,
            "15LTR": LTR15,
            "other": KG13,
        }
        return tis_count