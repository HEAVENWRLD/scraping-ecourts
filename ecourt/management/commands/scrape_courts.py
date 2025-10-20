from django.core.management.base import BaseCommand, CommandError
from ecourt.utils import ECourtsScraper
import json
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class Command(BaseCommand):
    help = 'Scrape eCourts data via command line'

    def add_arguments(self, parser):
        # Action arguments
        parser.add_argument(
            '--action',
            type=str,
            required=True,
            choices=['list-states', 'list-districts', 'list-complexes', 'list-courts', 
                    'search-case', 'download-cause-list', 'download-all'],
            help='Action to perform'
        )
        
        # Location arguments
        parser.add_argument('--state', type=str, help='State code')
        parser.add_argument('--district', type=str, help='District code')
        parser.add_argument('--complex', type=str, help='Court complex code')
        parser.add_argument('--court', type=str, help='Court code')
        
        # Case search arguments
        parser.add_argument('--cnr', type=str, help='CNR number')
        parser.add_argument('--case-type', type=str, help='Case type')
        parser.add_argument('--case-number', type=str, help='Case number')
        parser.add_argument('--case-year', type=str, help='Case year')
        
        # Date arguments
        parser.add_argument(
            '--date',
            type=str,
            help='Date in DD-MM-YYYY format (default: today)',
            default=datetime.now().strftime("%d-%m-%Y")
        )
        parser.add_argument(
            '--today',
            action='store_true',
            help='Use today\'s date'
        )
        parser.add_argument(
            '--tomorrow',
            action='store_true',
            help='Use tomorrow\'s date'
        )
        
        # Output arguments
        parser.add_argument(
            '--output',
            type=str,
            default='output',
            help='Output directory for JSON files (default: output/)'
        )
        parser.add_argument(
            '--downloads',
            type=str,
            default='downloads',
            help='Downloads directory for PDFs (default: downloads/)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        parser.add_argument(
            '--no-headless',
            action='store_true',
            help='Show browser window (disable headless mode)'
        )

    def handle(self, *args, **options):
        # Initialize scraper
        headless = not options['no_headless']
        verbose = options['verbose']
        scraper = ECourtsScraper(headless=headless, verbose=verbose)
        
        # Handle date
        if options['today']:
            date_str = datetime.now().strftime("%d-%m-%Y")
        elif options['tomorrow']:
            from datetime import timedelta
            date_str = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y")
        else:
            date_str = options['date']
        
        # Create output directories
        output_dir = options['output']
        downloads_dir = options['downloads']
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(downloads_dir, exist_ok=True)
        
        action = options['action']
        
        try:
            if action == 'list-states':
                self.handle_list_states(scraper, output_dir)
            
            elif action == 'list-districts':
                if not options['state']:
                    raise CommandError("--state is required for list-districts")
                self.handle_list_districts(scraper, options['state'], output_dir)
            
            elif action == 'list-complexes':
                if not options['state'] or not options['district']:
                    raise CommandError("--state and --district are required for list-complexes")
                self.handle_list_complexes(scraper, options['state'], 
                                          options['district'], output_dir)
            
            elif action == 'list-courts':
                if not options['state'] or not options['district'] or not options['complex']:
                    raise CommandError("--state, --district, and --complex are required for list-courts")
                self.handle_list_courts(scraper, options['state'], 
                                       options['district'], options['complex'], output_dir)
            
            elif action == 'search-case':
                if not options['state'] or not options['district'] or not options['complex']:
                    raise CommandError("--state, --district, and --complex are required")
                if not options['cnr'] and not (options['case_type'] and options['case_number'] and options['case_year']):
                    raise CommandError("Either --cnr or (--case-type, --case-number, --case-year) required")
                self.handle_search_case(scraper, options, output_dir)
            
            elif action == 'download-cause-list':
                if not all([options['state'], options['district'], 
                           options['complex'], options['court']]):
                    raise CommandError("--state, --district, --complex, and --court are required")
                self.handle_download_cause_list(scraper, options, date_str, downloads_dir, output_dir)
            
            elif action == 'download-all':
                if not all([options['state'], options['district'], options['complex']]):
                    raise CommandError("--state, --district, and --complex are required")
                self.handle_download_all(scraper, options, date_str, downloads_dir, output_dir)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise CommandError(str(e))

    def handle_list_states(self, scraper, output_dir):
        """Handle list-states action"""
        self.stdout.write(Fore.CYAN + "\n📍 Fetching States...\n")
        states = scraper.get_states()
        
        if states:
            self.stdout.write(Fore.GREEN + f"✓ Found {len(states)} states:\n")
            for state in states:
                self.stdout.write(f"  [{state['value']}] {state['text']}")
            
            # Save to JSON
            output_file = os.path.join(output_dir, 'states.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=2, ensure_ascii=False)
            self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")
        else:
            self.stdout.write(self.style.ERROR('✗ No states found'))

    def handle_list_districts(self, scraper, state_code, output_dir):
        """Handle list-districts action"""
        self.stdout.write(Fore.CYAN + f"\n📍 Fetching Districts for state: {state_code}\n")
        districts = scraper.get_districts(state_code)
        
        if districts:
            self.stdout.write(Fore.GREEN + f"✓ Found {len(districts)} districts:\n")
            for district in districts:
                self.stdout.write(f"  [{district['value']}] {district['text']}")
            
            output_file = os.path.join(output_dir, f'districts_state_{state_code}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(districts, f, indent=2, ensure_ascii=False)
            self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")
        else:
            self.stdout.write(self.style.ERROR('✗ No districts found'))

    def handle_list_complexes(self, scraper, state_code, district_code, output_dir):
        """Handle list-complexes action"""
        self.stdout.write(Fore.CYAN + f"\n📍 Fetching Court Complexes...\n")
        complexes = scraper.get_court_complexes(state_code, district_code)
        
        if complexes:
            self.stdout.write(Fore.GREEN + f"✓ Found {len(complexes)} court complexes:\n")
            for complex_item in complexes:
                self.stdout.write(f"  [{complex_item['value']}] {complex_item['text']}")
            
            output_file = os.path.join(output_dir, 
                                      f'complexes_state_{state_code}_dist_{district_code}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(complexes, f, indent=2, ensure_ascii=False)
            self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")
        else:
            self.stdout.write(self.style.ERROR('✗ No court complexes found'))

    def handle_list_courts(self, scraper, state_code, district_code, complex_code, output_dir):
        """Handle list-courts action"""
        self.stdout.write(Fore.CYAN + f"\n📍 Fetching Courts...\n")
        courts = scraper.get_courts(state_code, district_code, complex_code)
        
        if courts:
            self.stdout.write(Fore.GREEN + f"✓ Found {len(courts)} courts:\n")
            for court in courts:
                self.stdout.write(f"  [{court['value']}] {court['text']}")
            
            output_file = os.path.join(output_dir, 
                                      f'courts_s{state_code}_d{district_code}_c{complex_code}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(courts, f, indent=2, ensure_ascii=False)
            self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")
        else:
            self.stdout.write(self.style.ERROR('✗ No courts found'))

    def handle_search_case(self, scraper, options, output_dir):
        """Handle search-case action"""
        self.stdout.write(Fore.CYAN + "\n🔍 Searching for case...\n")
        
        result = scraper.search_case(
            options['state'],
            options['district'],
            options['complex'],
            cnr=options.get('cnr'),
            case_type=options.get('case_type'),
            case_number=options.get('case_number'),
            case_year=options.get('case_year')
        )
        
        if result.get('found'):
            self.stdout.write(Fore.GREEN + "✓ Case Found!\n")
            self.stdout.write(f"  Serial Number: {result.get('serial_number')}")
            self.stdout.write(f"  Court Name: {result.get('court_name')}")
            self.stdout.write(f"  Date: {result.get('date')}")
            
            if result.get('listed_today'):
                self.stdout.write(Fore.GREEN + "  ✓ Listed TODAY")
            if result.get('listed_tomorrow'):
                self.stdout.write(Fore.YELLOW + "  ⚠ Listed TOMORROW")
            
            if not result.get('listed_today') and not result.get('listed_tomorrow'):
                self.stdout.write(Fore.RED + "  ✗ NOT listed today or tomorrow")
        else:
            self.stdout.write(self.style.ERROR(f"✗ {result.get('message', 'Case not found')}"))
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'case_search_{timestamp}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")

    def handle_download_cause_list(self, scraper, options, date_str, downloads_dir, output_dir):
        """Handle download-cause-list action"""
        self.stdout.write(Fore.CYAN + f"\n📥 Downloading cause list for {date_str}...\n")
        
        success, message = scraper.download_cause_list(
            options['state'],
            options['district'],
            options['complex'],
            options['court'],
            date_str,
            downloads_dir
        )
        
        result = {
            'success': success,
            'message': message,
            'date': date_str,
            'state': options['state'],
            'district': options['district'],
            'complex': options['complex'],
            'court': options['court'],
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.stdout.write(Fore.GREEN + f"✓ {message}")
        else:
            self.stdout.write(Fore.RED + f"✗ {message}")
        
        # Save result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'download_result_{timestamp}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        self.stdout.write(Fore.YELLOW + f"💾 Saved to: {output_file}")

    def handle_download_all(self, scraper, options, date_str, downloads_dir, output_dir):
        """Handle download-all action"""
        self.stdout.write(Fore.CYAN + f"\n📥 Downloading cause lists for ALL courts on {date_str}...\n")
        
        results = scraper.download_all_courts_cause_list(
            options['state'],
            options['district'],
            options['complex'],
            date_str,
            downloads_dir
        )
        
        # Display results
        success_count = sum(1 for r in results if r.get('success'))
        total_count = len(results)
        
        self.stdout.write(Fore.GREEN + f"\n✓ Completed: {success_count}/{total_count} successful\n")
        
        for i, result in enumerate(results, 1):
            status = Fore.GREEN + "✓" if result.get('success') else Fore.RED + "✗"
            self.stdout.write(f"{status} [{i}/{total_count}] {result.get('court_name')}")
            self.stdout.write(f"    {result.get('message')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'download_all_{timestamp}.json')
        
        summary = {
            'date': date_str,
            'state': options['state'],
            'district': options['district'],
            'complex': options['complex'],
            'total_courts': total_count,
            'successful_downloads': success_count,
            'failed_downloads': total_count - success_count,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(Fore.YELLOW + f"\n💾 Saved to: {output_file}")
        self.stdout.write(Fore.CYAN + f"📁 PDFs downloaded to: {downloads_dir}/")
