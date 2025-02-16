def reg_message(code: str, language: str) -> str:
    english = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpendSplif Email Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 22px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
        .title {{
            text-align: center;
            font-size: 26px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">Welcome to SpendSplif</div>
        <div class="code">{code}</div>
        <p>Dear User,</p>
        <p>Welcome to SpendSplif - your reliable assistant in personal finance management. We are glad that you have joined our community and would like to confirm your account registration.</p>
        <p>To verify your email address, please enter the verification code above in the appropriate field in the application.</p>
        <p>After successful confirmation, you will be able to fully utilize all the features of SpendSplif for tracking income, controlling expenses, and achieving your financial goals.</p>
        <p>Feel free to contact us if you have any questions or need assistance. We are always happy to help!</p>
        <p>We wish you a pleasant and effective experience using SpendSplif!</p>
        <p>Sincerely,<br>The SpendSplif Team</p>
    </div>
</body>
</html>
        '''
    czech = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vítejte ve SpendSplif</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 22px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
        .title {{
            text-align: center;
            font-size: 26px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">Welcome to SpendSplif</div>
        <div class="code">{code}</div>
        <p>Vážený uživateli,</p>
        <p>Vítejte ve SpendSplif – vašem spolehlivém asistentovi pro správu osobních financí. Jsme rádi, že jste se připojili k naší komunitě, a rádi bychom potvrdili registraci vašeho účtu.</p>
        <p>Pro ověření vaší e-mailové adresy zadejte prosím výše uvedený ověřovací kód do příslušného pole v aplikaci.</p>
        <p>Po úspěšném potvrzení budete moci naplno využívat všechny funkce SpendSplif k sledování příjmů, kontrole výdajů a dosažení vašich finančních cílů.</p>
        <p>Pokud máte jakékoli dotazy nebo potřebujete pomoc, neváhejte nás kontaktovat. Vždy vám rádi pomůžeme!</p>
        <p>Přejeme vám příjemné a efektivní používání SpendSplif!</p>
        <p>S pozdravem,<br>Tým SpendSplif</p>
    </div>
</body>
</html>
        '''
    results_dict = {
        "english": english,
        "czech": czech
    }
    return results_dict[language.lower()]


def change_email_message(code: str, language: str) -> str:
    english = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpendSplif Email Verification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 22px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
        .title {{
            text-align: center;
            font-size: 26px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">Email Verification</div>
        <div class="code">{code}</div>
        <p>Please use the code above to verify your email change in the SpendSplif application.</p>
    </div>
</body>
</html>
        '''
    czech = f'''
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ověření e-mailu SpendSplif</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .code {{
            font-size: 22px;
            font-weight: bold;
            color: #FFA800;
            text-align: center;
            margin: 20px 0;
        }}
        .title {{
            text-align: center;
            font-size: 26px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">Ověření e-mailu</div>
        <div class="code">{code}</div>
        <p>Výše uvedený kód použijte k ověření změny e-mailu v aplikaci SpendSplif.</p>
    </div>
</body>
</html>
        '''
    result = {
        "english": english,
        "czech": czech
    }
    return result[language.lower()]


logout_success = {
    "english": {"message": "Logged out successfully"},
    "czech": {"message": "Odhlášení proběhlo úspěšně"}
}

custom_token_refresh = {
    "not_found": {
        "english": {"error": "Refresh token not found"},
        "czech": {"error": "Obnovovací token nebyl nalezen"}
    },
    "user_not_found": {
        "english": {"error": "User is inactive"},
        "czech": {"error": "Uživatel je neaktivní"}
    }
}