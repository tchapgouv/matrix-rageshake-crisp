import os
from dotenv import load_dotenv
from src.ConversationIdStorage import ConversationIdStorage
from datetime import datetime, timedelta
import logging

from src.job_process_invalid_rageshake import \
    process_conversation_from_rageshake, \
    extract_segment, \
    extract_platform_from_message, \
    extract_voip_context_from_message, \
    extract_domain_from_email, \
    extract_email_from_message, \
    extract_email_from_user_id, \
    extract_user_id_from_message
from src.utils import \
    has_tchap_team_answered, \
    get_conversation_meta, \
    get_conversation_origin_email, \
    get_conversations, \
    get_messages, \
    update_conversation_meta
from typing import Optional

SEGMENT_SEND_RESPONSE = "bot-send-response"

"""
This script is meant to be run every minute or so by a cron job
Its goal is to search for conversations in script which contains the rageshake@beta.gouv.fr 
and to replace it by the real email of the participant if it can be found in the discussion fields
"""


# load environment variables from .env file
load_dotenv()

CRISP_WEBSITE_ID = os.environ["CRISP_WEBSITE_ID"]
DEFAULT_EMAIL = os.environ.get("DEFAULT_EMAIL", "rageshake@tchap.gouv.fr")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"



def job_process_all_incoming_messages(from_minutes:int, processConversationIds:ConversationIdStorage):
    """
    Process not answered conversations by updating the email in it and setting segments
    An additional segment is set to trigger the send of the email
    
    Args:
    - processConversationIds: A ConversationIdStorage object containing the IDs of already processed conversations.
    - from_minutes: conversations will be gathered from a timestamp-from_minutes. Ie 20
    
    Returns: None
    """

    logging.debug(f'Start job_process_all_incoming_messages with from_minutes : {from_minutes}')

    # get conversations from last 20 minutes
    recent_conversations = get_conversations({
            "filter_date_end" : datetime.now(),
            "filter_date_start" : datetime.now() - timedelta(hours=1, minutes=from_minutes) #timezone...
        })
    
    for conversation in recent_conversations:
            conversation_id = conversation["session_id"]
            if not processConversationIds.has(conversation_id) and not has_tchap_team_answered(conversation_id):
                #if email is not correct
                if not is_email_valid(conversation_id):
                    logging.info(f'Process_conversation_from_rageshake : {conversation_id}')
                    process_conversation_from_rageshake(conversation_id, True)
                else:
                    #if email is correct
                    logging.info(f'Process_conversation_from_email : {conversation_id}')
                    process_conversation_from_email(conversation_id, True)
                
                processConversationIds.add(conversation_id)

    #logging.info(f'End job_process_all_incoming_messages')


def is_email_valid(conversation_id):
    conversation_email = get_conversation_origin_email(conversation_id=conversation_id)
    return conversation_email != None and conversation_email != DEFAULT_EMAIL


def segment_domain_from_email(email: str) -> Optional[str]:
    emails_to_sort = {
        # dgfip
        "@dgfip.finances.gouv.fr": 'dgfip',
        # finances-autres
        "@insee.fr": "finances-autre", 
        "@finances.gouv.fr": "finances-autre",
        "@dgtresor.gouv.fr": "finances-autre",
        "@dgccrf.finances.gouv.fr": "finances-autre",
        "@douane.finances.gouv.fr": "finances-autre",
        # education
        "@ac-versailles.fr": "education",
        "@ac-creteil.fr": "education",
        "@ac-paris.fr": "education",
        "@ac-nantes.fr": "education",
        "@ac-nancy-metz.fr": "education",
        "@ac-nice.fr": "education",
        "@ac-aix-marseille.fr": "education",
        "@ac-lille.fr": "education",
        "@ac-grenoble.fr": "education",
        "@ac-lyon.fr": "education",
        "@ac-montpellier.fr": "education",
        "@ac-bordeaux.fr": "education",
        "@ac-amiens.fr": "education",
        "@ac-orleans-tours.fr": "education",
        "@ac-toulouse.fr": "education",
        "@ac-strasbourg.fr": "education",
        "@ac-reims.fr": "education",
        "@ac-besancon.fr": "education",
        "@ac-caen.fr": "education",
        "@ac-clermont.fr": "education",
        "@ac-corse.fr": "education",
        "@ac-guyane.fr": "education",
        "@ac-guadeloupe.fr": "education",
        "@ac-reunion.fr": "education",
        "@ac-mayotte.fr": "education",
        "@ac-martinique.fr": "education",
        "@ac-limoges.fr": "education",
        "@ac-normandie.fr": "education",
        "@ac-poitiers.fr": "education",
        "@ac-reims.fr": "education",
        "@ac-rouen.fr": "education",
        "@ac-rennes.fr": "education",
        "@ac-noumea.nc": "education",
        "@education.gouv.fr": "education",
        "@ac-polynesie.pf": "education",
        # interieur
        "@interieur.gouv.fr": "interieur",
        # gendarmerie
        "@gendarmerie.interieur.gouv.fr": "gendarmerie",
        # social
        "@acoss.fr": "social",
        "@afld.fr": "social",
        "@agence-regionale-sante.fr": "social",
        "@agence-regionale-sante.gouv.fr": "social",
        "@agencebio.org": "social",
        "@agencedusport.fr": "social",
        "@ain-rhone.msa.fr": "social",
        "@alpesdunord.msa.fr": "social",
        "@alpesvaucluse.msa.fr": "social",
        "@alsace.msa.fr": "social",
        "@anses.fr": "social",
        "@ansm.sante.fr": "social",
        "@ansp.gouv.fr": "social",
        "@ap-hm.fr": "social",
        "@apa.gouv.fr": "social",
        "@aphp.fr": "social",
        "@ardechedromeloire.msa.fr": "social",
        "@arh44.sante.gouv.fr": "social",
        "@arh974.sante.gouv.fr": "social",
        "@armorique.msa.fr": "social",
        "@armorsante.bzh": "social",
        "@ars.gouv.fr": "social",
        "@ars.sante.fr": "social",
        "@assurance-maladie.fr": "social",
        "@assurance-maladie.gouv.fr": "social",
        "@auvergne.msa.fr": "social",
        "@baclesse.unicancer.fr": "social",
        "@bcl.msa.fr": "social",
        "@berry-touraine.msa.fr": "social",
        "@biep.gouv.fr": "social",
        "@biomedecine.fr": "social",
        "@bourgogne.msa.fr": "social",
        "@cab-emploi.gouv.fr": "social",
        "@cab-ville.gouv.fr": "social",
        "@cab.social-sante.gouv.fr": "social",
        "@cab.travail-sante.gouv.fr": "social",
        "@cab.travail.gouv.fr": "social",
        "@carsat-am.fr": "social",
        "@carsat-aquitaine.fr": "social",
        "@carsat-auvergne.fr": "social",
        "@carsat-bfc.fr": "social",
        "@carsat-bretagne.fr": "social",
        "@carsat-centre.fr": "social",
        "@carsat-centreouest.fr": "social",
        "@carsat-lr.fr": "social",
        "@carsat-mp.fr": "social",
        "@carsat-nordest.fr": "social",
        "@carsat-nordpicardie.fr": "social",
        "@carsat-normandie.fr": "social",
        "@carsat-pl.fr": "social",
        "@carsat-ra.fr": "social",
        "@carsat-sudest.fr": "social",
        "@ccmsa.msa.fr": "social",
        "@cgd13.fr": "social",
        "@cgss-guadeloupe.fr": "social",
        "@cgss-guyane.fr": "social",
        "@cgss-martinique.fr": "social",
        "@cgss.re": "social",
        "@cgss971.msa.fr": "social",
        "@cgss972.msa.fr": "social",
        "@cgss973.msa.fr": "social",
        "@cgss974.msa.fr": "social",
        "@ch-ag.fr": "social",
        "@ch-aiguilles.fr": "social",
        "@ch-airelys.fr": "social",
        "@ch-airesurlalys.fr": "social",
        "@ch-ajaccio.fr": "social",
        "@ch-alencon.fr": "social",
        "@ch-alpes-isere.fr": "social",
        "@ch-angely.fr": "social",
        "@ch-annecygenevois.fr": "social",
        "@ch-ardeche-nord.fr": "social",
        "@ch-ariege-couserans.fr": "social",
        "@ch-aubagne.fr": "social",
        "@ch-aubusson.fr": "social",
        "@ch-aurillac.fr": "social",
        "@ch-avignon.fr": "social",
        "@ch-avranches-granville.fr": "social",
        "@ch-bagneres.fr": "social",
        "@ch-beaune.fr": "social",
        "@ch-boispetit.fr": "social",
        "@ch-boscamnant.fr": "social",
        "@ch-bourges.fr": "social",
        "@ch-bourgOl.fr": "social",
        "@ch-bretagne-atlantique.fr": "social",
        "@ch-briancon.fr": "social",
        "@ch-brioude.fr": "social",
        "@ch-bsm.fr": "social",
        "@ch-bugeysud.fr": "social",
        "@ch-buzancais.fr": "social",
        "@ch-carcassonne.fr": "social",
        "@ch-carentan.fr": "social",
        "@ch-castelnaudary.fr": "social",
        "@ch-cavaillon.fr": "social",
        "@ch-cayenne.fr": "social",
        "@ch-cesame-angers.fr": "social",
        "@ch-chartres.fr": "social",
        "@ch-chatillon.fr": "social",
        "@ch-cholet.fr": "social",
        "@ch-claudinon.fr": "social",
        "@ch-cm.fr": "social",
        "@ch-cnp.fr": "social",
        "@ch-colmar.fr": "social",
        "@ch-condom.com": "social",
        "@ch-condom.fr": "social",
        "@ch-corbie.gouv.fr": "social",
        "@ch-cotebasque.fr": "social",
        "@ch-coutances.fr": "social",
        "@ch-de-eu.fr": "social",
        "@ch-denain.fr": "social",
        "@ch-dieppe.fr": "social",
        "@ch-douarnenez.fr": "social",
        "@ch-dromevivarais.fr": "social",
        "@ch-dunkerque.fr": "social",
        "@ch-embrun.fr": "social",
        "@ch-epsylan.fr": "social",
        "@ch-erdreloire.fr": "social",
        "@ch-esquirol-limoges.fr": "social",
        "@ch-ewa.fr": "social",
        "@ch-falaise.fr": "social",
        "@ch-fecamp.fr": "social",
        "@ch-felleries-liessies.fr": "social",
        "@ch-fidesien.fr": "social",
        "@ch-gdaumezon.fr": "social",
        "@ch-gisors.fr": "social",
        "@ch-givors.fr": "social",
        "@ch-guise.fr": "social",
        "@ch-ham.com": "social",
        "@ch-havre.fr": "social",
        "@ch-hopitauxduleman.fr": "social",
        "@ch-hvsm.fr": "social",
        "@ch-jonzac.fr": "social",
        "@ch-laigle.fr": "social",
        "@ch-lannemezan.fr": "social",
        "@ch-laon.fr": "social",
        "@ch-layon-aubance.fr": "social",
        "@ch-lepuy.fr ": "social",
        "@ch-limoux.fr": "social",
        "@ch-lisieux.fr": "social",
        "@ch-lourdes.fr": "social",
        "@ch-metropole-savoie.fr": "social",
        "@ch-meximieux.ght01.fr": "social",
        "@ch-Montauban.fr": "social",
        "@ch-montreuil.fr": "social",
        "@ch-morlaix.fr": "social",
        "@ch-mortagne.fr": "social",
        "@ch-pau.fr": "social",
        "@ch-pdv.ght01.fr": "social",
        "@ch-peronne.fr": "social",
        "@ch-poitiers.fr": "social",
        "@ch-pont-audemer.fr": "social",
        "@ch-redon.fr": "social",
        "@ch-riom.fr": "social",
        "@ch-rives.fr": "social",
        "@ch-roanne.fr": "social",
        "@ch-rodez.fr": "social",
        "@ch-royan.fr": "social",
        "@ch-saint-esprit.fr": "social",
        "@ch-saint-tropez.fr": "social",
        "@ch-saintnazaire.fr": "social",
        "@ch-saintomer.fr": "social",
        "@ch-saintonge.fr": "social",
        "@ch-saintvaleryencaux.fr": "social",
        "@ch-salon.fr": "social",
        "@ch-sarreguemines.fr": "social",
        "@ch-saumur.fr": "social",
        "@ch-sees.fr": "social",
        "@ch-sens.fr": "social",
        "@ch-sesame-angers.fr": "social",
        "@ch-st-yrieix.fr": "social",
        "@ch-stjunien.fr": "social",
        "@ch-stlaurent.com": "social",
        "@ch-stlo.fr": "social",
        "@ch-stlo.fr": "social",
        "@ch-stomer.fr": "social",
        "@ch-tarbes-vic.fr": "social",
        "@ch-tourcoing.fr": "social",
        "@ch-tullins.fr": "social",
        "@ch-valvert.fr": "social",
        "@ch-vichy.fr": "social",
        "@ch-vienne.fr": "social",
        "@ch-yssingeaux.fr": "social",
        "@ch-yssingeaux.fr": "social",
        "@ch-zuydcoote.fr": "social",
        "@cham-savoie.fr": "social",
        "@charentes.msa.fr": "social",
        "@chb.unicancer.fr": "social",
        "@chbd-laragne.fr": "social",
        "@chdes2rives.fr": "social",
        "@chdouelafontaine.fr": "social",
        "@chi-cvs.fr": "social",
        "@chi-elbeuf-louviers.fr": "social",
        "@chi-fsr.fr": "social",
        "@chi-val-ariege.fr": "social",
        "@chicacr.fr": "social",
        "@chicas-gap.fr": "social",
        "@chimb.fr": "social",
        "@chipr.fr": "social",
        "@chph0l.fr": "social",
        "@chpyr.fr": "social",
        "@chr-metz-thionville.fr": "social",
        "@chru-nancy.fr": "social",
        "@chru-strasbourg.fr": "social",
        "@chs-sarreguemines.fr": "social",
        "@chs-savoie.fr": "social",
        "@chsa.fr": "social",
        "@chturenne.fr": "social",
        "@chu-amiens.fr": "social",
        "@chu-angers.fr": "social",
        "@chu-bordeaux.fr": "social",
        "@chu-brest.fr": "social",
        "@chu-clermontferrand.fr": "social",
        "@chu-dijon.fr": "social",
        "@chu-grenoble.fr": "social",
        "@chu-guadeloupe.fr": "social",
        "@chu-lille.fr": "social",
        "@chu-limoges.fr ": "social",
        "@chu-lyon.fr": "social",
        "@chu-martinique.fr": "social",
        "@chu-montpellier.fr": "social",
        "@chu-nantes.fr": "social",
        "@chu-nimes.fr": "social",
        "@chu-poitiers.fr": "social",
        "@chu-rennes.fr": "social",
        "@chu-st-etienne.fr": "social",
        "@chu-toulouse.fr": "social",
        "@chuse.fr": "social",
        "@chvm.fr": "social",
        "@ci.handicap.gouv.fr": "social",
        "@ciivise.gouv.fr": "social",
        "@cjml.fr": "social",
        "@cn.medecin.fr": "social",
        "@cnaf.fr": "social",
        "@cnav.fr": "social",
        "@cnds.sports.gouv.fr": "social",
        "@cnefop.gouv.fr": "social",
        "@competences-inclusion.emploi.gouv.fr ": "social",
        "@concours.social.gouv.fr": "social",
        "@contribution.gouv.fr": "social",
        "@cotesnormandes.msa.fr": "social",
        "@cpo-alencon.net": "social",
        "@cps-stbarth.msa.fr": "social",
        "@creps-auvergne.sports.gouv.fr": "social",
        "@creps-bordeaux.sports.gouv.fr": "social",
        "@creps-centre.sports.gouv.fr": "social",
        "@creps-dijon.sports.gouv.fr": "social",
        "@creps-guadeloupe.sports.gouv.fr": "social",
        "@creps-idf.sports.gouv.fr": "social",
        "@creps-lorraine.sports.gouv.fr": "social",
        "@creps-montpellier.sports.gouv.fr": "social",
        "@creps-nancy.sports.gouv.fr": "social",
        "@creps-pap.sports.gouv.fr": "social",
        "@creps-pdl.sports.gouv.fr": "social",
        "@creps-poitiers.sports.gouv.fr": "social",
        "@creps-reims.sports.gouv.fr": "social",
        "@creps-reunion.sports.gouv.fr": "social",
        "@creps-strasbourg.sports.gouv.fr": "social",
        "@creps-sudest.sports.gouv.fr": "social",
        "@creps-toulouse.sports.gouv.fr": "social",
        "@creps-vichy.sports.gouv.fr": "social",
        "@creps-wattignies.sports.gouv.fr": "social",
        "@cu": "social",
        "@dac-23-87.fr": "social",
        "@dcstep.gouv.fr": "social",
        "@ddc.social.gouv.fr": "social",
        "@declarations-pharmacie.ars.sante.fr ": "social",
        "@deets.gouv.fr": "social",
        "@dieccte.gouv.fr": "social",
        "@dif.gouv.fr": "social",
        "@diffusion.jeunesse-sports.gouv.fr": "social",
        "@diffusion.service-civique.gouv.fr": "social",
        "@diffusion.travail.gouv.fr": "social",
        "@diffusion.ville-jeunesse-sports.gouv.fr": "social",
        "@diges.gouv.fr": "social",
        "@direccte.gouv.fr": "social",
        "@dlg.msa.fr": "social",
        "@dmp.gouv.fr": "social",
        "@domepsch.fr": "social",
        "@dreets.gouv.fr": "social",
        "@drieets.gouv.fr": "social",
        "@drjscs.gouv.fr": "social",
        "@droits-femmes.gouv.fr": "social",
        "@economie-solidaire.gouv.fr": "social",
        "@efs.sante.fr": "social",
        "@ehpad-havre.fr": "social",
        "@ehpad-luneray.fr": "social",
        "@ehpad-saintcrespin.fr": "social",
        "@ehpadlauzerte.fr": "social",
        "@elections-professionnelles.travail.gouv.fr ": "social",
        "@emploi.gouv.fr": "social",
        "@emploidesseniors.gouv.fr": "social",
        "@engagement-civique.gouv.fr": "social",
        "@ensm.sports.gouv.fr": "social",
        "@envsn.sports.gouv.fr": "social",
        "@epas65.fr": "social",
        "@epd-les2monts.fr": "social",
        "@epide.fr": "social",
        "@epms-le-littoral.net": "social",
        "@epms-le-littoral.org": "social",
        "@eps-etampes.fr": "social",
        "@epsm-marne.fr": "social",
        "@epsm-metz-jury.fr": "social",
        "@epsm-quimper.fr": "social",
        "@esante-hdf.fr": "social",
        "@esante-martinique.fr": "social",
        "@esante.gouv.fr": "social",
        "@esante.si-samu.fr": "social",
        "@esbv.fr": "social",
        "@esea-na.fr": "social",
        "@externes.deets.gouv.fr": "social",
        "@externes.dreets.gouv.fr": "social",
        "@externes.drieets.gouv.fr": "social",
        "@externes.engagement-civique.gouv.fr": "social",
        "@externes.sante.gouv.fr": "social",
        "@externes.service-civique.gouv.fr": "social",
        "@fabrique.social.gouv.fr": "social",
        "@famille-enfance.gouv.fr": "social",
        "@famille.gouv.fr": "social",
        "@feddf.gouv.fr": "social",
        "@femmes-egalite.gouv.fr": "social",
        "@femmes.gouv.fr": "social",
        "@femmesegalite.gouv.fr": "social",
        "@fiva.fr": "social",
        "@formation.gouv.fr": "social",
        "@franchecomte.msa.fr": "social",
        "@fvjs.gouv.fr": "social",
        "@geodae.sante.gouv.fr": "social",
        "@gh-artoisternois.fr": "social",
        "@gh-msm.fr": "social",
        "@ghba.fr": "social",
        "@ghbs.bzh": "social",
        "@ghrmsa.fr": "social",
        "@ght-caux-maritime.fr": "social",
        "@ght-cdn.fr": "social",
        "@ght-guadeloupe.fr": "social",
        "@ght-hautebretagne.fr": "social",
        "@ght-hgto.fr": "social",
        "@ght-rouergue.fr": "social",
        "@ght-saintonge.fr": "social",
        "@ght01.fr": "social",
        "@ght18.fr": "social",
        "@ght43.fr": "social",
        "@ght82.fr": "social",
        "@ghtcantal.fr": "social",
        "@ghtducher.fr": "social",
        "@ghu-paris.fr": "social",
        "@gipes.fr": "social",
        "@gipsudmarne.fr": "social",
        "@grandsud.msa.fr": "social",
        "@grippea-h1n1.sante.gouv.fr": "social",
        "@handicap.gouv.fr": "social",
        "@has-sante.fr": "social",
        "@hautenormandie.msa.fr": "social",
        "@hcf-famille.fr": "social",
        "@hcf.famille.gouv.fr": "social",
        "@hci.pm.gouv.fr": "social",
        "@hihl.fr": "social",
        "@hipr44.fr": "social",
        "@hl-corcoue.fr": "social",
        "@hl-saintromain.fr": "social",
        "@hli-presquile.fr": "social",
        "@hno.fr": "social",
        "@hopital-belleme.fr": "social",
        "@hopital-craponne.fr ": "social",
        "@hopital-foch.com": "social",
        "@hopital-le-montaigu.com": "social",
        "@hopital-lecorbusier.fr": "social",
        "@hopital-sevre-loire.fr": "social",
        "@hopitaldugier.fr": "social",
        "@hopitalpse.fr": "social",
        "@hopitaux-de-provence.fr": "social",
        "@hopitaux-jura.fr": "social",
        "@hopitaux-ubayens.fr": "social",
        "@hoplangeac.fr ": "social",
        "@hstv.fr": "social",
        "@hstv.gouv.fr": "social",
        "@idda13.fr": "social",
        "@ifce.fr": "social",
        "@ifce.sports.gouv.fr": "social",
        "@igas.gouv.fr": "social",
        "@imsa.msa.fr": "social",
        "@injep.fr": "social",
        "@insep.fr": "social",
        "@insep.sports.gouv.fr": "social",
        "@institutcancer.fr": "social",
        "@integration.gouv.fr": "social",
        "@ints.fr": "social",
        "@Jeunesse-solidarites-actives.gouv.fr": "social",
        "@jeunesse-sports.gouv.fr": "social",
        "@jeunesse-vie-associative.gouv.fr": "social",
        "@languedoc.msa.fr": "social",
        "@lesvertesannees.fr": "social",
        "@lhopitalnordouest.fr": "social",
        "@limousin.msa.fr": "social",
        "@lorraine.msa.fr": "social",
        "@lrva.fr": "social",
        "@lyshyrome.fr": "social",
        "@maisoncohesionsociale.gouv.fr": "social",
        "@mam.msa.fr": "social",
        "@mayenne-orne-sarthe.msa.fr": "social",
        "@medecine-de-proximite.fr": "social",
        "@memoiresante.gouv.fr": "social",
        "@metiersdugrandage.gouv.fr": "social",
        "@mildt.premier-ministre.gouv.fr": "social",
        "@mipih.fr": "social",
        "@miprof.gouv.fr": "social",
        "@monrdvdroitdutravail.travail.gouv.fr": "social",
        "@monrdvdroitsocial.direccte.gouv.fr": "social",
        "@mpn.msa.fr": "social",
        "@mps.msa.fr": "social",
        "@msa10-52.msa.fr": "social",
        "@msa20.msa.fr": "social",
        "@msa33.msa.fr": "social",
        "@msa44-85.msa.fr": "social",
        "@msa49.msa.fr": "social",
        "@msa59-62.msa.fr": "social",
        "@msa75.msa.fr": "social",
        "@nh-navarre.fr": "social",
        "@normand-esante.fr": "social",
        "@observatoire-parite.gouv.fr": "social",
        "@okantis.fr ": "social",
        "@oniam.fr": "social",
        "@ordre.medecin.fr": "social",
        "@oscar.service-civique.gouv.fr": "social",
        "@pca.social.gouv.fr ": "social",
        "@pegase.sg.social.gouv.fr": "social",
        "@personnes-agees.gouv.fr": "social",
        "@personnesagees.gouv.fr": "social",
        "@pharma-si.ars.sante.fr": "social",
        "@picardie.msa.fr": "social",
        "@point-info-famille.fr": "social",
        "@pointinfofamille.fr": "social",
        "@poitou.msa.fr": "social",
        "@politique-ville.gouv.fr": "social",
        "@portesdebretagne.msa.fr": "social",
        "@precarite.gouv.fr": "social",
        "@provence-azur.msa.fr": "social",
        "@reforme-assurance-maladie.gouv.fr": "social",
        "@reims.unicancer.fr": "social",
        "@res-belleetoile.fr": "social",
        "@retraites.gouv.fr": "social",
        "@saint nzaire": "social",
        "@sante-ara.fr": "social",
        "@sante-famille-handicap.gouv.fr": "social",
        "@sante-jeunesse-sports.gouv.fr": "social",
        "@sante-sports.gouv.fr": "social",
        "@sante-travail.gouv.fr": "social",
        "@sante.gouv.fr": "social",
        "@santepubliquefrance.fr": "social",
        "@sdli.ars.sante.fr": "social",
        "@service-civique.gouv.fr": "social",
        "@servicesalapersonne.gouv.fr": "social",
        "@SI-VIC.sante.gouv.fr ": "social",
        "@sib.fr": "social",
        "@sih09.fr": "social",
        "@silpc.fr": "social",
        "@sirec.ars.sante.fr": "social",
        "@social-sante.gouv.fr": "social",
        "@social.gouv.fr": "social",
        "@solidarite.gouv.fr": "social",
        "@sports.gouv.fr": "social",
        "@sportsdenature.gouv.fr": "social",
        "@sudaquitaine.msa.fr": "social",
        "@terminologie.jeunesse-sports.gouv.fr": "social",
        "@transformation.social.gouv.fr": "social",
        "@transparence-sante.gouv.fr": "social",
        "@travail-emploi-sante.gouv.fr": "social",
        "@travail-sante.gouv.fr": "social",
        "@travail.gouv.fr": "social",
        "@unisante.fr": "social",
        "@univ-tlse2.fr": "social",
        "@urssaf.fr": "social",
        "@ville-jeunesse-sports.gouv.fr": "social",
        "@ville.gouv.fr": "social",
        "@vjs.gouv.fr": "social"
    }

    # convert email to lowercase
    email = email.lower()

    # iterate through domains list to find segment
    for key, value in emails_to_sort.items():
        if email.endswith(key):
            return value
        
    # no domain matches in the list. Return None
    return None



# process a conversation 
# if email is invalid (rageshake) it is reset
# segments are set in conversation
# An additional segment SEGMENT_SEND_RESPONSE is set to trigger the send of the email
# this method is copied from "job_process_invalid_rageshake.process_conversation"
# should be refactored
def process_conversation_from_email(conversation_id:str, verbose=False) -> bool:
    try:
        if verbose: 
            logging.debug(f"# Extract data from {conversation_id}")
        messages = get_messages(conversation_id)
        #first_message = messages[0]["content"]
        message_contents = list(map(lambda message: str(message["content"]), messages))  # Extract the "content" field from each message
        combined_messages = "".join(message_contents).replace("\n","")  # Concatenate the message contents together into a single string

        if verbose: 
            logging.debug(f"all messages : {combined_messages}")

        # try to grab email to extract domain
        email = extract_email_from_message(combined_messages)
        userId = extract_user_id_from_message(combined_messages)

        if not email or email == 'undefined':
            email = extract_email_from_user_id(userId)

        if not email or email == 'undefined':
            email = get_conversation_origin_email(conversation_id)

        if verbose: 
            logging.debug(f"found in {conversation_id}: userId: {userId}, email {email}")

        # if email of user is correct (not the default one) continue with segments
        logging.debug(f"Email is correct in conversation : {conversation_id}")
        segment = extract_segment(combined_messages)
        #add segment SEGMENT_SEND_RESPONSE to activate the bot workflow send response
        #this workflow is : "on Segment update - envoie message"
        segments =[segment, SEGMENT_SEND_RESPONSE]
        platform = extract_platform_from_message(combined_messages)
        if platform:
            segments.append(platform)
        voip_context = extract_voip_context_from_message(combined_messages)
        if voip_context:
            segments.append(voip_context)
        domain = segment_domain_from_email(email)
        if domain:
            segments.append(domain)
        # conversation should be in "unresolved" state before updating segments
        # change_conversation_state(conversation_id, "unresolved")
        update_conversation_meta(conversation_id=conversation_id, segments=segments)
        return True
    except Exception as e:
        #do not fail script
        logging.error(f"error in {conversation_id} : {e}")
        return False  
