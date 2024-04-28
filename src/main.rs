// VRV: a service for visualising how parties vote in the swedish parliament

// TODO:
// 1. Get data from riksdagen.se
// 2. Parse data
// 3. Visualise data


struct Request {
    url: String,
    method: String,
    headers: Vec<String>,
    body: String,
}

// example of a request
//  https://data.riksdagen.se/voteringlista/?bet=&punkt=&valkrets=&rost=&iid=&sz=500&utformat=HTML&gruppering=

enum Rost {
    Ja,
    Nej,
    Avstar,
    Franvarande,
}

enum Utformat {
    HTML,
    XML,
    JSON,
}

enum Gruppering {
    VoteringId,
    Punkt,
    Votering,
    Parti,
    Rost,
    LedamotId,
    Efternamn,
    Tilltalsnamn,
    Valkrets,
    Iort,
    Banknummer,
    Kon,
    Fodd,
    Status,
    PersonUrlXml,
    BildUrl80,
    BildUrlMax,
}

fn match_utformat(utformat: Utformat) -> String {
    match utformat {
        Utformat::HTML => "HTML",
        Utformat::XML => "XML",
        Utformat::JSON => "JSON",
    }.to_string()
}

fn match_gruppering(gruppering: Gruppering) -> String {
    match gruppering {
        Gruppering::VoteringId => "votering_id",
        Gruppering::Punkt => "punkt",
        Gruppering::Votering => "votering",
        Gruppering::Parti => "parti",
        Gruppering::Rost => "rost",
        Gruppering::LedamotId => "ledamot_id",
        Gruppering::Efternamn => "efternamn",
        Gruppering::Tilltalsnamn => "tilltalsnamn",
        Gruppering::Valkrets => "valkrets",
        Gruppering::Iort => "iort",
        Gruppering::Banknummer => "banknummer",
        Gruppering::Kon => "kon",
        Gruppering::Fodd => "fodd",
        Gruppering::Status => "status",
        Gruppering::PersonUrlXml => "person_url_xml",
        Gruppering::BildUrl80 => "bild_url_80",
        Gruppering::BildUrlMax => "bild_url_max",
    }.to_string()
}

fn match_rost(rost: Rost) -> String {
    match rost {
        Rost::Ja => "Ja",
        Rost::Nej => "Nej",
        Rost::Avstar => "Avstår",
        Rost::Franvarande => "Frånvarande",
    }.to_string()
}

fn form_request(gruppering: Gruppering, rost: Rost) -> Request {
    let base_url = "https://data.riksdagen.se/voteringlista/";
    let method = "GET";
    let body = String::new();

    let mut headers = Vec::new();
    headers.push("Accept: application/json".to_string());

    let gruppering_str = format!("gruppering={}", match_gruppering(gruppering));
    headers.push(gruppering_str);

    let rost_str = format!("rost={}", match_gruppering(rost));
    headers.push(rost_str);

    let utformat_str = "utformat=JSON";
    headers.push(utformat_str);

    Request {
        url: url.to_string(),
        method: method.to_string(),
        headers: headers,
        body: body,
    }
}


fn main() {

    // make request and save response to file
    let request = form_request(Gruppering::VoteringId, Rost::Ja);

    let mut easy = Easy::new();
    easy.url(&request.url).unwrap();

    let mut headers = List::new();

    for header in request.headers {
        headers.append(&header).unwrap();
    }

    easy.http_headers(headers).unwrap();

    let mut transfer = easy.transfer();
    transfer.write_function(|data| {
        Ok(stdout().write(data).unwrap())
    }).unwrap();

    transfer.perform().unwrap();

    // save response to file
    let mut file = File::create("response.json").unwrap();
    transfer.write_function(|data| {
        Ok(file.write(data).unwrap())
    }).unwrap();

    transfer.perform().unwrap();

    // do visualisation with python script "visualise.py"
    let output = Command::new("python")
        .arg("visualise.py")
        .output()
        .expect("failed to execute process");

    
}
