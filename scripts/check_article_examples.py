#!/usr/bin/env python3
"""Compile the Java snippets published in the archive and run behavioral regressions."""
from pathlib import Path
import re
import subprocess
import tempfile

ARTICLES = Path('src/content/posts/ko')
CASES = {
    'NewId': '2021-07-19-new-id.md', 'Pair': '2021-07-20-pair-delete.md',
    'Dot': '2021-07-22-dot-product.md', 'Signs': '2021-07-22-plus-minus.md',
    'Words': '2021-07-23-number-word.md', 'Runner': '2021-07-23-unsuccessful-runner.md',
    'Failure': '2021-07-24-fail-percentage.md', 'Interval': '2021-07-29-interval-num.md',
    'Pokemon': '2021-07-29-ponkemon.md', 'Cache': '2021-08-17-cache.md',
}
BILINGUAL = {'2021-07-19-new-id.md', '2021-07-22-dot-product.md',
             '2021-07-23-number-word.md', '2021-08-17-cache.md',
             '2021-07-20-pair-delete.md', '2021-07-23-unsuccessful-runner.md',
             '2021-07-24-fail-percentage.md', '2021-07-29-ponkemon.md',
             '2021-07-22-plus-minus.md', '2021-07-29-interval-num.md'}
HARNESS = r'''
import java.util.*;
import java.util.stream.*;
class ArticleExamples {
 static int assertions=0;
 static void eq(Object actual,Object expected){ assertions++; if(!Objects.deepEquals(actual,expected))throw new AssertionError("actual="+actual+", expected="+expected); }
 static String newId(String s){
   StringBuilder b=new StringBuilder();
   for(char ch:s.toCharArray()){
     char c=ch>='A'&&ch<='Z'?(char)(ch+32):ch;
     if((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'||c=='_'||c=='.'){
       if(c!='.'||b.length()==0||b.charAt(b.length()-1)!='.')b.append(c);
     }
   }
   if(b.length()>0&&b.charAt(0)=='.')b.deleteCharAt(0);
   if(b.length()>0&&b.charAt(b.length()-1)=='.')b.deleteCharAt(b.length()-1);
   if(b.length()==0)b.append('a');
   if(b.length()>15)b.setLength(15);
   if(b.charAt(b.length()-1)=='.')b.deleteCharAt(b.length()-1);
   while(b.length()<3)b.append(b.charAt(b.length()-1));
   return b.toString();
 }
 static int pair(String s){String previous;do{previous=s;s=s.replace("aa","").replace("bb","").replace("cc","");}while(!s.equals(previous));return s.isEmpty()?1:0;}
 static int[] failure(int n,int[] stages){
   long[] hits=new long[n+1],totals=new long[n+1];
   for(int i=1;i<=n;i++)for(int s:stages){if(s==i)hits[i]++;if(s>=i)totals[i]++;}
   Integer[] order=IntStream.rangeClosed(1,n).boxed().toArray(Integer[]::new);
   Arrays.sort(order,(a,b)->{long left=hits[a]*(totals[b]==0?1:totals[b]);long right=hits[b]*(totals[a]==0?1:totals[a]);return left==right?Integer.compare(a,b):Long.compare(right,left);});
   return Arrays.stream(order).mapToInt(Integer::intValue).toArray();
 }
 static int cache(int size,String[] cities){
   // Deliberately use a list-based reference, separate from the published map.
   List<String> entries=new ArrayList<>();int cost=0;
   for(String city:cities){String key=city.toLowerCase(Locale.ROOT);int old=entries.indexOf(key);cost+=old<0?5:1;if(old>=0)entries.remove(old);entries.add(key);if(entries.size()>size)entries.remove(0);}
   return cost;
 }
 static void cacheSequences(String[] values,int position){
   if(position==values.length){for(int size=0;size<=3;size++)eq(new Cache().solution(size,values),cache(size,values));return;}
   for(String city:new String[]{"A","a","B","C"}){values[position]=city;cacheSequences(values,position+1);}
 }
 static void idSequences(String value,int remaining){
   if(remaining==0){
     String actual=new NewId().solution(value),other=new NewIdVersion2().solution(value);
     eq(actual,newId(value));eq(other,actual);
     eq(actual.length()>=3&&actual.length()<=15,true);
     eq(actual.matches("[a-z0-9_-]+(?:[.][a-z0-9_-]+)*"),true);
     eq(new NewId().solution(actual),actual);eq(new NewIdVersion2().solution(other),other);return;
   }
   for(char c:new char[]{'A','I','0','.','!','_','-'})idSequences(value+c,remaining-1);
 }
 static void pairSequences(String value,int remaining){
   if(remaining==0){eq(new Pair().solution(value),pair(value));return;}
   for(char c:new char[]{'a','b','c'})pairSequences(value+c,remaining-1);
 }
 static void runnerSequences(String[] names,int position){
   if(position==names.length){
     for(int missing=0;missing<names.length;missing++){
       String[] completion=new String[names.length-1];int target=0;
       for(int i=names.length-1;i>=0;i--)if(i!=missing)completion[target++]=names[i];
       eq(new Runner().solution(names.clone(),completion),names[missing]);
     }
     return;
   }
   for(String name:new String[]{"ana","bob","cam"}){names[position]=name;runnerSequences(names,position+1);}
 }
 static void failureSequences(int levels,int[] stages,int position){
   if(position==stages.length){eq(new Failure().solution(levels,stages.clone()),failure(levels,stages));return;}
   for(int stage=1;stage<=levels+1;stage++){stages[position]=stage;failureSequences(levels,stages,position+1);}
 }
 static int pokemonBySelections(int[] nums){
   // Fixture IDs are 1..3 and length is at most 8. Enumerate actual position choices.
   int best=0;
   for(int mask=0;mask<(1<<nums.length);mask++)if(Integer.bitCount(mask)==nums.length/2){
     boolean[] seen=new boolean[4];int kinds=0;
     for(int i=0;i<nums.length;i++)if((mask&(1<<i))!=0&&!seen[nums[i]]){seen[nums[i]]=true;kinds++;}
     best=Math.max(best,kinds);
   }
   return best;
 }
 static void pokemonSequences(int[] nums,int position){
   if(position==nums.length){eq(new Pokemon().solution(nums.clone()),pokemonBySelections(nums));return;}
   for(int kind=1;kind<=3;kind++){nums[position]=kind;pokemonSequences(nums,position+1);}
 }
 static void signSequences(int[] values,boolean[] signs,int position,long sum){
   if(position==values.length){eq(new Signs().solution(values,signs),(int)sum);return;}
   for(int value=1;value<=3;value++)for(boolean positive:new boolean[]{false,true}){
     values[position]=value;signs[position]=positive;
     signSequences(values,signs,position+1,sum+(positive?value:-value));
   }
 }
 static long[] sequenceByAddition(int x,int n){
   long[] result=new long[n];long value=0;
   for(int i=0;i<n;i++){value+=x;result[i]=value;}return result;
 }
 public static void main(String[] args){
   Locale.setDefault(Locale.forLanguageTag("tr-TR"));
   eq(new NewId().solution("...!@BaT#*..y.abcdefghijklm"),"bat.y.abcdefghi");
   eq(new NewId().solution("I"),"iii");
   eq(new Dot().solution(new int[]{1,2,3,4},new int[]{-3,-1,0,2}),3);
   eq(new Failure().solution(5,new int[]{2,1,2,6,2,4,3,3}),new int[]{3,4,2,1,5});
   eq(new Failure().solution(5,new int[]{6,6}),new int[]{1,2,3,4,5});
   eq(new Interval().solution(10000000,1000)[999],10000000000L);
   eq(new Cache().solution(2,new String[]{"Jeju","Pangyo","Jeju","Seoul","Pangyo"}),21);
   eq(new Pair().solution("aa".repeat(500000)),1);
   Random r=new Random(20261024);
   String alphabet="ABCIZabc123-_.!@";
   String[] words={"zero","one","two","three","four","five","six","seven","eight","nine"};
   for(int trial=0;trial<500;trial++){
     StringBuilder name=new StringBuilder(),letters=new StringBuilder();
     for(int i=0;i<1+r.nextInt(60);i++)name.append(alphabet.charAt(r.nextInt(alphabet.length())));
     for(int i=0;i<r.nextInt(30);i++)letters.append((char)('a'+r.nextInt(3)));
     eq(new NewId().solution(name.toString()),newId(name.toString()));
     eq(new NewIdVersion2().solution(name.toString()),newId(name.toString()));
     eq(new Pair().solution(letters.toString()),pair(letters.toString()));
     int n=1+r.nextInt(20),dot=0,signed=0;int[] a=new int[n],b=new int[n],absolute=new int[n];boolean[] signs=new boolean[n];
     for(int i=0;i<n;i++){a[i]=r.nextInt(2001)-1000;b[i]=r.nextInt(2001)-1000;dot+=a[i]*b[i];absolute[i]=1+r.nextInt(1000);signs[i]=r.nextBoolean();signed+=signs[i]?absolute[i]:-absolute[i];}
     eq(new Dot().solution(a,b),dot);eq(new Signs().solution(absolute,signs),signed);
     int number=1+r.nextInt(1000000000);StringBuilder encoded=new StringBuilder();
     for(char d:Integer.toString(number).toCharArray())encoded.append(r.nextBoolean()?words[d-'0']:Character.toString(d));
     eq(new Words().solution(encoded.toString()),number);
     String[] participants=new String[n];for(int i=0;i<n;i++)participants[i]="name"+r.nextInt(5);
     List<String> completed=new ArrayList<>(Arrays.asList(participants));String missing=completed.remove(0);Collections.shuffle(completed,r);
     eq(new Runner().solution(participants,completed.toArray(new String[0])),missing);
     int levels=1+r.nextInt(10);int[] stages=new int[n];for(int i=0;i<n;i++)stages[i]=1+r.nextInt(levels+1);
     eq(new Failure().solution(levels,stages),failure(levels,stages));
     int x=r.nextInt(20000001)-10000000;long[] expected=new long[n];for(int i=0;i<n;i++)expected[i]=(long)x*(i+1);
     eq(new Interval().solution(x,n),expected);
     int[] pokemon=new int[2*n];Set<Integer> kinds=new HashSet<>();for(int i=0;i<pokemon.length;i++){pokemon[i]=1+r.nextInt(20);kinds.add(pokemon[i]);}
     eq(new Pokemon().solution(pokemon),Math.min(n,kinds.size()));
     String[] cities=new String[n];for(int i=0;i<n;i++)cities[i]=(r.nextBoolean()?"CITY":"city")+r.nextInt(5);
     int size=r.nextInt(6);eq(new Cache().solution(size,cities),cache(size,cities));
   }
   for(int length=0;length<=6;length++)cacheSequences(new String[length],0);
   for(int length=1;length<=4;length++)idSequences("",length);
   String[] repeatedCity=new String[100000];Arrays.fill(repeatedCity,"Jeju");
   eq(new Cache().solution(0,repeatedCity),500000);eq(new Cache().solution(1,repeatedCity),100004);
   String[] distinctCities=new String[31];for(int i=0;i<31;i++)distinctCities[i]="City"+(char)('A'+i/26)+(char)('A'+i%26);
   eq(new Cache().solution(30,distinctCities),155);
   eq(new NewId().solution("A".repeat(300)),"a".repeat(15));eq(new NewIdVersion2().solution("A".repeat(300)),"a".repeat(15));
   int[] maxA=new int[1000],maxB=new int[1000];Arrays.fill(maxA,1000);Arrays.fill(maxB,1000);
   eq(new Dot().solution(maxA,maxB),1000000000);Arrays.fill(maxA,-1000);eq(new Dot().solution(maxA,maxB),-1000000000);
   eq((long)50000*50000,2500000000L);eq((long)(50000*50000),-1794967296L);
   eq(new Words().solution("two"+"zero".repeat(9)),2000000000);
   eq(new Words().solution("one4seveneight"),1478);eq(new Words().solution("23four5six7"),234567);eq(new Words().solution("123"),123);
   for(String input:new String[]{"abcdefghijklmn.op","=.="}){eq(new NewId().solution(input),newId(input));eq(new NewIdVersion2().solution(input),newId(input));}
   for(int length=1;length<=8;length++)pairSequences("",length);
   for(int length=1;length<=5;length++)runnerSequences(new String[length],0);
   for(int levels=1;levels<=4;levels++)for(int length=1;length<=5;length++)failureSequences(levels,new int[length],0);
   for(int length=2;length<=8;length+=2)pokemonSequences(new int[length],0);
   eq(new Pair().solution("ab".repeat(500000)),0);eq(new Pair().solution("a"),0);eq(new Pair().solution("baabaa"),1);
   String[] manyRunners=new String[100000];Arrays.fill(manyRunners,"ana");eq(new Runner().solution(manyRunners,Arrays.copyOf(manyRunners,99999)),"ana");
   int[] manyPlayers=new int[200000];Arrays.fill(manyPlayers,500);int[] lateFirst=new int[500];lateFirst[0]=500;for(int i=1;i<500;i++)lateFirst[i]=i;
   eq(new Failure().solution(500,manyPlayers),lateFirst);Arrays.fill(manyPlayers,501);eq(new Failure().solution(500,manyPlayers),IntStream.rangeClosed(1,500).toArray());
   eq(new Failure().solution(3,new int[]{1,1,1}),new int[]{1,2,3});
   int[] manyTypes=IntStream.rangeClosed(1,10000).toArray();eq(new Pokemon().solution(manyTypes),5000);Arrays.fill(manyTypes,7);eq(new Pokemon().solution(manyTypes),1);
   for(int length=1;length<=5;length++)signSequences(new int[length],new boolean[length],0,0);
   for(int x=-12;x<=12;x++)for(int n=1;n<=20;n++)eq(new Interval().solution(x,n),sequenceByAddition(x,n));
   int[] magnitudes=new int[1000];Arrays.fill(magnitudes,1000);boolean[] signs=new boolean[1000];
   eq(new Signs().solution(magnitudes,signs),-1000000);Arrays.fill(signs,true);eq(new Signs().solution(magnitudes,signs),1000000);
   eq(new Signs().solution(new int[]{4,7,12},new boolean[]{true,false,true}),9);
   eq(new Signs().solution(new int[]{1,2,3},new boolean[]{false,false,true}),0);
   for(int x:new int[]{-10000000,0,10000000})eq(new Interval().solution(x,1000),sequenceByAddition(x,1000));
   System.out.println("[ok] 11 published Java solutions compiled; "+assertions+" behavioral assertions passed (including Turkish locale, ties, overflow, exhaustive small cases, and idempotence).");
 }
}
'''


def main():
    with tempfile.TemporaryDirectory(prefix='youdozi-article-tests-') as directory:
        tmp=Path(directory);sources=[]
        for name,file in CASES.items():
            blocks=re.findall(r'```java\n([\s\S]*?)\n```',(ARTICLES/file).read_text())
            blocks=[b for b in blocks if 'solution(' in b]
            if not blocks:raise ValueError(f'No solution snippet in {file}')
            if file in BILINGUAL:
                english=re.findall(r'```java\n([\s\S]*?)\n```',(Path('src/content/posts/en')/file).read_text())
                english=[b for b in english if 'solution(' in b]
                if english!=blocks:raise ValueError(f'English/Korean solutions differ in {file}')
            for i,body in enumerate(blocks):
                classname=name if i==0 else f'{name}Version{i+1}'
                path=tmp/f'{classname}.java'
                if re.search(r'\bpublic class Solution\b',body):
                    # Preserve the article's imports and complete class, changing only
                    # its name to compile multiple independent solutions together.
                    path.write_text(re.sub(r'\bpublic class Solution\b','public class '+classname,body,count=1)+'\n')
                else:
                    path.write_text('import java.util.*;\nimport java.util.Map.Entry;\nimport java.util.function.*;\nimport java.util.stream.*;\nclass '+classname+' {\n'+body+'\n}\n')
                sources.append(str(path))
        harness=tmp/'ArticleExamples.java';harness.write_text(HARNESS);sources.append(str(harness))
        subprocess.run(['javac','--release','11','-encoding','UTF-8','-d',str(tmp),*sources],check=True)
        subprocess.run(['java','-cp',str(tmp),'ArticleExamples'],check=True,timeout=30)
        print('[ok] Ten English/Korean article pairs contain identical complete Java solutions.')
        scripts=re.findall(r'```(?:bash|sh)\n([\s\S]*?)\n```',(ARTICLES/'2023-11-17-linux-shellscript-version-compare.md').read_text())
        if not scripts:raise ValueError('No runnable version-comparison shell snippet found')
        script=scripts[0]
        file=tmp/'compare.sh';file.write_text(script)
        for a,b,operator in [('1.2','1.2.0','='),('1.1000','2.0','<'),('1.2.3.4.5','1.2.3.4.4','>'),('99999999999999999999','2','>')]:
            result=subprocess.run(['bash',str(file),a,b],capture_output=True,text=True,check=True)
            assert result.stdout.strip()==f'{a} {operator} {b}'
        for values in [[],['1'],['1.2-rc1','1.2'],['1;echo bad','2']]:
            result=subprocess.run(['bash',str(file),*values],capture_output=True,text=True)
            assert result.returncode==2
        print('[ok] Published version-comparison shell snippet: 8 behavioral cases passed.')

if __name__=='__main__':main()
