# Libraries
import datetime
import os

import click
from flask.cli import with_appcontext

# register other models
from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client, ClientType
# register flask specific extensions
from Groot.Database.models.CurrentQueue import Queue
from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Database.models.MarketDataModel import MarketData
from Groot.Database.models.MicrophoneModel import Microphone
from Groot.Database.models.Role import Role
from Groot.Database.models.Session import Session
from Groot.Database.models.ShareClass import ShareClass
from Groot.Database.models.ShareClassNAV import ShareClassNAV
from Groot.Database.models.Speech2TextModuleModel import Speech2TextModuleModel
from Groot.Database.models.VisualizationModel import Visualization
from Groot.Extensions.DatabaseExtension import db


# to init db do the following commands
# > $env:FLASK_APP = "groot.py"
# > flask init-db

# to init db do the following commands
# > $env:FLASK_APP = "groot.py"
# > flask init-db


@click.command('init-db')
@with_appcontext
def init_db_command():
    if not click.confirm('Do you want to delete the current data?'):
        click.echo('Abort')
        return

    click.echo('Initializes Database')
    init_db()
    click.echo('Created new data base')

    if not click.confirm('Should Dummy data be inserted?'):
        return

    click.echo('Start inserting Dummy data')
    input_dummy_data_in_db()
    click.echo('Dummy data is inserted')

    if not click.confirm('Do you want to load financial data?'):
        click.echo('Abort')
        return

    click.echo('Start inserting Dummy data')
    load_financial_data()
    click.echo('Dummy data is inserted')


@click.command('load-shcl-data')
@with_appcontext
def load_shcl_data():
    data_path = f'{os.getcwd()}/Groot/Data/'
    ShareClass.load_csv(f'{data_path}DVS-Export.csv')
    # ShareClassNAV.load_csv(F'{data_path}dShareClassNAV_VFCH.csv')
    print('Finished loading VF CH data')
    ShareClassNAV.load_csv(f'{data_path}dShareClassNAV_VF.csv')
    print('Finished loading VF data')
    # ShareClassNAV.load_csv(f'{data_path}dShareClassNAV_VFII.csv')

    print('Finished loading VF II data')
    print('nr of records:')
    print(ShareClassNAV.get_nr())


@with_appcontext
def init_db():
    db.drop_all()
    db.create_all()


def load_financial_data():
    data_path = "Groot/Data/"

    ShareClass.load_csv(f'{data_path}DVS-Export.csv')
    print('Finished loading Share Class data')

    ShareClassNAV.load_csv(f'{data_path}dShareClassNAV_VF.csv')
    print('Finished loading VF data')

    ShareClassNAV.load_csv(f'{data_path}dShareClassNAV_VFII.csv')
    print('Finished loading VF II data')

    ShareClassNAV.load_csv(f'{data_path}dShareClassNAV_VFCH.csv')
    print('Finished loading VF CH data')

    MarketData.load_csv(f'{data_path}dSMI_Values.csv', 'SMI')
    print('Finished loading SMI Data')

    MarketData.load_csv(f'{data_path}dBTC.csv', 'Bitcoin')
    print('finished loading BTC rates')

    MarketData.load_csv(f'{data_path}dTreasuryYields.csv', 'Bonds')
    print('finished loading Bond Data')

    MarketData.load_csv(f'{data_path}dCommodities.csv', 'Commodities')
    print('finished loading Commodity Data')

    MarketData.load_csv(f'{data_path}dCPI.csv', 'CPI')
    print('finished loading Inflation')

    MarketData.load_csv(f'{data_path}dVWDAX.csv', 'Return VW - DAX', return_in_percent=True)
    MarketData.load_csv(f'{data_path}dVWNYSE.csv', 'Return VW - NYSE', return_in_percent=True)
    print('finished loading Currency Risk')


def input_dummy_data_in_db():
    u1 = ClientAdvisor(username="Hans Zimmermann",
                       password="123456", role=Role.admin.name, accepted=True)
    u1.save()
    u2 = ClientAdvisor(username="Max Muster", password="123456",
                       role=Role.advisor.name, accepted=False)
    u2.save()
    print_add(u2)
    u3 = ClientAdvisor(username="Peter Meier", password="123456",
                       role=Role.advisor.name, accepted=True)
    u3.save()
    print_add(u3)
    u4 = ClientAdvisor(username="Nadia Müller", password="123456",
                       role=Role.guest.name, accepted=False)
    u4.save()

    u5 = ClientAdvisor(username="admin", password="admin",
                       role=Role.admin.name, accepted=True)
    u5.save()

    # ========== add clients ==========

    address_c1 = {
        'street': 'Moosstrasse',
        'street_nr': 67,
        'zip_code': 8038,
        'city': 'Zurich',
        'country': 'CH'
    }

    address_c2 = {
        'street': 'Langstrasse',
        'street_nr': 15,
        'zip_code': 8004,
        'city': 'Zurich',
        'country': 'CH'
    }

    address_c3 = {
        'street': 'Seestrasse',
        'street_nr': 65,
        'zip_code': 8002,
        'city': 'Zurich',
        'country': 'CH'
    }

    c1 = Client(firstname='Andy',
                lastname='Aidoo',
                email='andy@aidoo.io',
                address=address_c1,
                birthdate=datetime.datetime(1998, 11, 22),
                nr_of_counseling=0,
                AuM=1000,
                currency='CHF',
                client_advisor_uuid=u5.uuid,
                client_type=ClientType.RETAIL.name)
    c1.save()

    c2 = Client(firstname='Lance',
                lastname='Stephenson',
                email='lance@steph.io',
                address=address_c2,
                birthdate=datetime.datetime(1982, 1, 5),
                nr_of_counseling=0,
                AuM=10400,
                currency='USD',
                client_advisor_uuid=u4.uuid,
                client_type=ClientType.RETAIL.name)
    c2.save()

    c3 = Client(firstname='Mike',
                lastname='Tyson',
                email='mike@tyson.io',
                address=address_c3,
                birthdate=datetime.datetime(1976, 4, 18),
                nr_of_counseling=0,
                AuM=4500000,
                currency='CHF',
                client_advisor_uuid=u5.uuid,
                client_type=ClientType.PROFESSIONAL.name)
    c3.save()

    print('Adding: ', c1, '\n', c2, '\n', c3)

    session1 = Session(
        transcript="Blabalabdlfbdfslkfsdkfjlkösjfsadfskldfjkllkjflkjdfsdsjkl",
        start_time=datetime.datetime.now(),
        stop_time=datetime.datetime.now(),
        client=c1,
        client_advisor=u1,
        completed=True
    )

    u5.sessions = [session1]
    u5.update()

    # ========== add financial jargon ==========

    term = FinancialJargon(subject="Bond",
                           synonyms=[],
                           description="Bonds are long-term lending agreements between a borrower and a lender. For "
                                       "example, when a municipality (such as a city, county, town, or village) needs "
                                       "to build new roads or a hospital, it issues bonds to finance the project. "
                                       "Corporations generally issue bonds to raise money for capital expenditures, "
                                       "operations, and acquisitions.",
                           long_description="The selling price of bonds, like publicly traded stock, is normally set "
                                            "by what the market will bear. The issuer of the bond sets the interest "
                                            "rate, which is known as the stated, coupon, face, contract, or nominal "
                                            "rate. All five terms mean the same thing — the interest rate given in "
                                            "the bond indenture\n\nYou can compare a bond indenture to any type of "
                                            "legal financing document that you may have signed to finance a house or "
                                            "car. It describes the key terms of the bond issuance, such as maturity "
                                            "date and interest rate.\n\nThe people who purchase a bond receive "
                                            "interest payments during the bond’s term (or for as long as they hold "
                                            "the bond) at the bond’s stated interest rate. When the bond matures (the "
                                            "term of the bond expires), the company pays back the bondholder the "
                                            "bond’s face value.\n\nA bond is either a source of financing or an "
                                            "investment, depending on which side of the transaction you’re looking "
                                            "at. Because this is a chapter on long-term liabilities, it looks at this "
                                            "transaction from the source of financing viewpoint.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='ISIN',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying="Bonds" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Development of AuM if all the money had been invested in three-years treasury rate.'
    )
    visualization.save()

    term = FinancialJargon(subject="Stock",
                           synonyms=[],
                           description="A stock is a general term used to describe the ownership certificates of any "
                                       "company. A share, on the other hand, refers to the stock certificate of a "
                                       "particular company. Holding a particular company's share makes you a "
                                       "shareholder.",
                           long_description="Stocks are of two types—common and preferred. The difference is while "
                                            "the holder of the former has voting rights that can be exercised in "
                                            "corporate decisions, the later doesn't. However, preferred shareholders "
                                            "are legally entitled to receive a certain level of dividend payments "
                                            "before any dividends can be issued to other shareholders.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='ISIN',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying="SMI" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Development of AuM if all the money had been invested into an SMI-tracker ETF.'
    )
    visualization.save()

    term = FinancialJargon(subject="Commodity",
                           synonyms=[],
                           description="The basic idea is that there is little differentiation between a commodity "
                                       "coming from one producer and the same commodity from another producer. A "
                                       "barrel of oil is basically the same product, regardless of the producer. By "
                                       "contrast, for electronics merchandise, the quality and features of a given "
                                       "product may be completely different depending on the producer.",
                           long_description="Some traditional examples of commodities include grains, gold, beef, "
                                            "oil, and natural gas. More recently, the definition has expanded to "
                                            "include financial products, such as foreign currencies and indexes. "
                                            "Technological advances have also led to new types of commodities being "
                                            "exchanged in the marketplace. For example, cell phone minutes and "
                                            "bandwidth.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='ISIN',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying="Commodities" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Development of AuM if all the money had been invested in $COMT'
    )
    visualization.save()

    term = FinancialJargon(subject="Crypto Currency",
                           synonyms=["digital currency", "Gold 2.0", "peer-to-peer money",
                                     "DeFi", "decentralized money", "decentralized finance"],
                           description="Cryptocurrency is a digital payment system that doesn't rely on banks to "
                                       "verify transactions. It’s a peer-to-peer system that can enable anyone "
                                       "anywhere to send and receive payments. Instead of being physical money "
                                       "carried around and exchanged in the real world, cryptocurrency payments exist "
                                       "purely as digital entries to an online database describing specific "
                                       "transactions. When you transfer cryptocurrency funds, the transactions are "
                                       "recorded in a public ledger. Cryptocurrency is stored in digital wallets.",
                           long_description="Cryptocurrency received its name because it uses encryption to verify "
                                            "transactions. This means advanced coding is involved in storing and "
                                            "transmitting cryptocurrency data between wallets and to public ledgers. "
                                            "The aim of encryption is to provide security and safety.\n\nThe first "
                                            "cryptocurrency was Bitcoin, which was founded in 2009 and remains the "
                                            "best known today. Much of the interest in cryptocurrencies is to trade "
                                            "for profit, with speculators at times driving prices skyward.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)
    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying = "Bitcoin" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Development a AuM if all the money had been invested into BTC.'
    )
    visualization.save()

    term = FinancialJargon(subject="Hedging",
                           synonyms=[],
                           description="A hedge is an investment that is made with the intention of reducing the risk "
                                       "of adverse price movements in an asset. Normally, a hedge consists of taking "
                                       "an offsetting or opposite position in a related security.",
                           long_description="Hedging is somewhat analogous to taking out an insurance policy. If you "
                                            "own a home in a flood-prone area, you will want to protect that asset "
                                            "from the risk of flooding—to hedge it, in other words—by taking out "
                                            "flood insurance. In this example, you cannot prevent a flood, "
                                            "but you can plan ahead of time to mitigate the dangers in the event that "
                                            "a flood did occur.\n\nThe most common way of hedging in the investment "
                                            "world is through derivatives. Derivatives are securities that move in "
                                            "correspondence to one or more underlying assets. They include options, "
                                            "swaps, futures and forward contracts. The underlying assets can be "
                                            "stocks, bonds, commodities, currencies, indices or interest rates. "
                                            "Derivatives can be effective hedges against their underlying assets, "
                                            "since the relationship between the two is more or less clearly defined. "
                                            "It’s possible to use derivatives to set up a trading strategy in which a "
                                            "loss for one investment is mitigated or offset by a gain in a comparable "
                                            "derivative.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    term = FinancialJargon(subject="Market Capitalization",
                           synonyms=["capitalization",
                                     "capitalisation", "market capitalisation"],
                           description="Market cap—or market capitalization—refers to the total value of all a "
                                       "company's shares of stock. It is calculated by multiplying the price of a "
                                       "stock by its total number of outstanding shares. For example, a company with "
                                       "20 million shares selling at CHF 50 a share would have a market cap of CHF 1 "
                                       "billion.",
                           long_description="Why is market capitalization such an important concept? It allows "
                                            "investors to understand the relative size of one company versus another. "
                                            "Market cap measures what a company is worth on the open market, "
                                            "as well as the market's perception of its future prospects, because it "
                                            "reflects what investors are willing to pay for its stock.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    term = FinancialJargon(subject="Inflation",
                           synonyms=["economic slump", "burst of growth"],
                           description="Inflation is the rate of increase in prices over a given period of time. "
                                       "Inflation is typically a broad measure, such as the overall increase in "
                                       "prices or the increase in the cost of living in a country.",
                           long_description="But it can also be more narrowly calculated—for certain goods, such as "
                                            "food, or for services, such as a haircut, for example. Whatever the "
                                            "context, inflation represents how much more expensive the relevant set "
                                            "of goods and/or services has become over a certain period, most commonly "
                                            "a year.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying = "CPI" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Decline of purchasing power if the current AuM had been saved for the last ten years.'
    )
    visualization.save()

    term = FinancialJargon(subject="Market Risk",
                           synonyms=["systemic risk"],
                           description="Market risk is the possibility that an individual or other entity will "
                                       "experience losses due to factors that affect the overall performance of "
                                       "investments in the financial markets.",
                           long_description="\t-Market risk, or systematic risk, affects the performance of the "
                                            "entire market simultaneously.\n\tMarket risk cannot be eliminated "
                                            "through diversification.\n\tSpecific risk, or unsystematic risk, "
                                            "involves the performance of a particular security and can be mitigated "
                                            "through diversification.\n\tMarket risk may arise due to changes to "
                                            "interest rates, exchange rates, geopolitical events, "
                                            "or recessions.\nMarket risk, also called systematic risk, "
                                            "cannot be eliminated through diversification, though it can be hedged in "
                                            "other ways. Sources of market risk include recessions, political "
                                            "turmoil, changes in interest rates, natural disasters, and terrorist "
                                            "attacks. Systematic, or market risk, tends to influence the entire "
                                            "market at the same time.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Value',
        data_source_filter_column='ISIN',
        data_source_filter_values='',
        viz_query=f'SELECT date, rate FROM {MarketData.__table__.name} WHERE underlying="SMI" AND date > "2007-03-01" AND date < "2009-06-01" ORDER BY date ASC',
        x_axis='Date',
        y_axis='Value',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='Value',
        tid=term.tid,
        description='Extract of SMI druring the 2008 financial crisis.'
    )
    visualization.save()

    term = FinancialJargon(subject="Currency Risk",
                           synonyms=[],
                           description="Currency risk, commonly referred to as exchange-rate risk, arises from the "
                                       "change in price of one currency in relation to another. Investors or "
                                       "companies that have assets or business operations across national borders are "
                                       "exposed to currency risk that may create unpredictable profits and losses.",
                           long_description="Currency risk can be reduced by hedging, which offsets currency "
                                            "fluctuations. If a Swiss investor holds stocks in Germany, for example, "
                                            "the realized return is affected by both the change in stock prices and "
                                            "the change in the value of the EUR against the CHF. If a 15% return on "
                                            "German stocks is realized and the EUR depreciates 15% against the CHF, "
                                            "the investor breaks even, minus associated trading costs.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='COMPOSITE_SCATTERPLOT',
        data_source_table=f'{MarketData.__table__.name}',
        data_source_columns=f'Date,Underlying,Return',
        data_source_filter_column='underlying',
        data_source_filter_values='LU1176839154,LU0120694640,LU0153585053',
        viz_query=f'SELECT date, underlying, monthly_return FROM {MarketData.__table__.name} WHERE (underlying = "Return VW - DAX" OR underlying = "Return VW - NYSE")',
        x_axis='Date',
        y_axis='Return',
        group_label='Underlying',
        personalization_source='',
        personalization_target='',
        tid=term.tid,
        description='Comparison of VW returns (in percent) in the stock exchanges DAX and NYSE'
    )
    visualization.save()
    print_add(visualization)

    term = FinancialJargon(subject="Cluster Risk",
                           synonyms=[],
                           description="A cluster risk is when specific risks accumulate in your portfolio; for "
                                       "example, if you have invested half of your investment capital in shares in a "
                                       "single company, sector or region. If the share price falls or an entire "
                                       "sector or region suffers a downturn, a large part of the capital you invested "
                                       "is affected.",
                           long_description="To avoid such risk, you should diversify your portfolio. This means "
                                            "ensuring your investment capital is not too heavily weighted in "
                                            "investments in individual companies, markets, currencies or sectors, "
                                            "etc. The easiest and most affordable way to achieve that is through "
                                            "investment funds.",
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    term = FinancialJargon(subject='Maximum Draw Down',
                           synonyms=[],
                           description='A maximum drawdown (MDD) is the maximum observed loss from a peak to a trough '
                                       'of a portfolio, before a new peak is attained. Maximum drawdown is an '
                                       'indicator of downside risk over a specified time period.',
                           long_description='A maximum drawdown (MDD) is the maximum observed loss from a peak to a '
                                            'trough of a portfolio, before a new peak is attained. Maximum drawdown '
                                            'is an indicator of downside risk over a specified time period.',
                           calculations_necessary=['maximum_draw_down']
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='SCATTERPLOT',
        data_source_table=f'{ShareClassNAV.__table__.name}',
        data_source_columns=f'NAVDate,NAV,ISIN',
        data_source_filter_column='ISIN',
        data_source_filter_values='LU1176839154',
        viz_query=f'SELECT NAVDate, NAV, ISIN FROM {ShareClassNAV.__table__.name} WHERE ISIN = "LU0105717663" ORDER BY ISIN ASC, NAVDate ASC',
        x_axis='NAVDate',
        y_axis='NAV',
        group_label='',
        personalization_source='client.AuM',
        personalization_target='NAV',
        tid=term.tid,
        description='Development of AuM if all the money had been invested in "Vontobel Fund - Absolute Return Bond (EUR) A". Maximum Draw Down corresponds to 18%'
    )
    visualization.save()
    print_add(visualization)

    term = FinancialJargon(subject='Risk-Return-Profile',
                           synonyms=["risk return tradeoff"],
                           description='The risk return profile, or risk return tradeoff, describes the principle that usually stocks with low risk also yield low return in the long term. Similarly, stocks with high risk tend to yield high returns in the long term. However, there can be no guarantee that this holds for every investment product.',
                           long_description='The risk return profile, or risk return tradeoff, describes the principle that usually stocks with low risk also yield low return in the long term. Similarly, stocks with high risk tend to yield high returns in the long term. However, there can be no guarantee that this holds for every investment product.',
                           calculations_necessary=['']
                           )
    term.save()
    print_add(term)

    visualization = Visualization(
        visualization_type='MULTI_SCATTERPLOT',
        data_source_table=f'{ShareClassNAV.__table__.name}',
        data_source_columns=f'NAVDate,NAV,ISIN',
        data_source_filter_column='ISIN',
        data_source_filter_values='LU1176839154,LU0120694640,LU0153585053',
        viz_query=f'SELECT NAVDate, NAV, ISIN FROM {ShareClassNAV.__table__.name} WHERE (ISIN = "LU1176839154" OR ISIN = "LU0120694640" OR ISIN = "LU0153585053") ORDER BY ISIN ASC, NAVDate ASC',
        x_axis='NAVDate',
        y_axis='NAV',
        group_label='ISIN',
        personalization_source='client.AuM',
        personalization_target='NAV',
        tid=term.tid,
        description='Development of AuM if all the money had been invested in, "Vontobel Fund - Swiss Money A", "Vontobel Fund - European Equity A", "Variopartner SICAV - Sectoral Biotech Opportunities Fund I"'
    )
    visualization.save()
    print_add(visualization)

    term = FinancialJargon(subject='ESG Investing',
                           synonyms=['ESG', 'environmental', 'social', 'governance'],
                           description='ESG stands for "environmental, social, and governance". ESG investing is an investment strategy that invests in companies based on their commitment to one or more of the ESG factors. The commitment is usually measured via scores that get computed by independent third-party companies or research groups.',
                           long_description='ESG stands for "environmental, social, and governance". ESG investing is an investment strategy that invests in companies based on their commitment to one or more of the ESG factors. The commitment is usually measured via scores that get computed by independent third-party companies or research groups.',
                           calculations_necessary=[]
                           )
    term.save()
    print_add(term)

    term_recognized = Queue(client_advisor=u5.username, terms=["cluster risk"])
    term_recognized.save()
    print_add(term_recognized)

    term_recognized = Queue(client_advisor=u5.username, terms=[
        "cluster risk", "return", "background risk", "Commodities", "market capitalization"])
    term_recognized.save()
    print_add(term_recognized)

    term_recognized = Queue(client_advisor=u5.username, terms=["inflation"])
    term_recognized = term_recognized.save()
    print_add(term_recognized)

    # ========== add microphones ==========

    mic1 = Microphone(name='Groot 1',
                      ip='localhost',
                      port=2000)

    mic1.save()

    mic2 = Microphone(name='Groot 2',
                      ip='some other address',
                      port=2000)

    mic2.save()

    print('Adding:\n', mic1, '\n', mic2)

    # ========== add speech2text modules ==========

    module1 = Speech2TextModuleModel(name='AssemblyAI', selected=False)
    module1.save()
    module2 = Speech2TextModuleModel(name='Google', selected=False)
    module2.save()
    module2 = Speech2TextModuleModel(name='Mock_Script', selected=True)
    module2.save()

    print('Adding:\n', module1, '\n', module2)


def print_add(object):
    print(f'Added: {object}')
