import io
import boto3
import json
import csv
from collections import defaultdict

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    bucket = 'jorge-aulademo'
    key = 'Fifa_world_cup_matches.csv'
    obj = s3.Object(bucket, key)
    body = obj.get()['Body'].read().decode('utf-8')
   
    csv_reader = csv.DictReader(io.StringIO(body))
    goals_by_team = defaultdict(int)
    for row in csv_reader:
        team1 = row['team1']
        team2 = row['team2']
        goals_team1 = int(row['number of goals team1'])
        goals_team2 = int(row['number of goals team2'])
        
        goals_by_team[team1] += goals_team1
        goals_by_team[team2] += goals_team2
    
    sorted_teams = sorted(goals_by_team.items(), key=lambda x: x[1], reverse=True)
    
    team_objects = [{"team": team, "goals": goals} for team, goals in sorted_teams]
        
    return {
        "statusCode": 200,
        "body": json.dumps(team_objects)
    }