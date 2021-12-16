import datetime
import click
from inc import moex, db, an

def timediff(start : datetime):
    d = datetime.datetime.now() - start
    return datetime.datetime.fromtimestamp(d.total_seconds()).strftime("%M:%S")

@click.command()
def get_bonds():
    """
    Парсинг всех (вкл не торгуемые) облигаций, кот отдает ISS MOEX
    и добавление в базу или обновление в базе
    минимальное колво инфы по каждой их облиг
    :return:
    """
    start_time = datetime.datetime.now()

    # обновление списка облиг
    # добавление новых, смена статуса и т.д.
    # без спеков и доходностей - только secid, isin, boiard id n etc.
    for p in range(1, 1000):
        bonds = moex.get_bonds(p, 100)

        if len(bonds) < 1:
            click.secho(f"Закончила обновлять список облигаций на стр. № {p}", fg='green')
            break

        [db.add_bond(j) for j in bonds]
        db.session.commit()
        click.echo( click.style(timediff(start_time), fg='yellow') + f" / page {p}")

    # добаляю спеки облиги (их тоже нужно обновлять, напр за дату след купона)
    # добалвю расчет доходностей yields (кот мосбиржа считает раз в сутки по пред дню)
    # считаю только те что is_traded = True, это ~2700 из 8000 облиг
    while True:
        bond = db.get_next_bond(60*60*24)
        if not bond:
            click.secho(f"Закончила обновлять", fg='green')
            break

        db.update_bond_from_json(bond, moex.get_specs(bond.secid))
        db.update_bond_from_json(bond, moex.get_yield(bond.secid))
        db.session.commit()

        click.echo( click.style(timediff(start_time), fg='yellow') + " / " + str(bond))

@click.command()
def stats():
    for k, v in an.get_main_stats().items():
        click.echo(click.style(k, fg='bright_white') + " .. " + click.style(v, fg='green'))

@click.command()
@click.option('--rep', '-r', default='lowest_price', show_default=True, required=False)
def report(rep="lowest_price"):
    method = getattr(an, f"report_{rep}")
    df = method()

    # df = an.report_lowest_price()
    # df = an.report_365_yieldest()
    # df = an.report_365_cheap_ll21()

    for i, r in df.iterrows():
        print(f"{r['shortname']}, {r['matdays'].days} : {r['price']}, {r['effectiveyield']} / https://www.moex.com/ru/issue.aspx?code={r['secid']}")

    click.echo("report %s, нашла %s облиг" % (
        click.style(f"{rep}", fg='green'),
        click.style(f"{len(df)}", fg='green')
    ))

@click.command()
def test():
    b = db.get_random_bond()
    j = moex.get_yield(b.secid)

    db.update_bond_from_json(b, j)
    db.session.commit()
    click.echo([j, b.primary_boardid])


@click.group()
def cli_group():
    pass

cli_group.add_command(report)
cli_group.add_command(stats)
cli_group.add_command(get_bonds)
cli_group.add_command(test)