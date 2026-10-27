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
   LinkedHashMap<String,Boolean> map=new LinkedHashMap<>(16,.75f,true);int cost=0;
   for(String city:cities){String key=city.toLowerCase(Locale.ROOT);cost+=map.get(key)==null?5:1;map.put(key,true);if(map.size()>size)map.remove(map.keySet().iterator().next());}
   return cost;
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
   System.out.println("[ok] 11 published Java snippets compiled; "+assertions+" behavioral assertions passed (including Turkish locale, ties, and overflow).");
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
            for i,body in enumerate(blocks):
                classname=name if i==0 else f'{name}Version{i+1}'
                path=tmp/f'{classname}.java'
                path.write_text('import java.util.*;\nimport java.util.Map.Entry;\nimport java.util.function.*;\nimport java.util.stream.*;\nclass '+classname+' {\n'+body+'\n}\n')
                sources.append(str(path))
        harness=tmp/'ArticleExamples.java';harness.write_text(HARNESS);sources.append(str(harness))
        subprocess.run(['javac','--release','11','-encoding','UTF-8','-d',str(tmp),*sources],check=True)
        subprocess.run(['java','-cp',str(tmp),'ArticleExamples'],check=True,timeout=30)
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
